from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    SAFE_METHODS, AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import RecipeFilterSet
from .paginator import PagePaginator
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (CreateRecipeSerializer, CustomUserSerializer,
                          FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)
from .utils import generate_pdf

from recipes.models import (Favorite, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import Follow, User


class CustomUserViewSet(UserViewSet):
    """
    Кастомный юзер вьюсет.
    """
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    serializer_class = CustomUserSerializer
    pagination_class = PagePaginator

    def perform_create(self, serializer):
        hash_pwd = make_password(serializer.validated_data.get('password'))
        serializer.save(password=hash_pwd)

    @action(methods=['post'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        """Функция подписки на автора."""

        author = get_object_or_404(User, pk=id)

        if request.user == author:
            return Response({
                'errors': "Нельзя подписаться на самого себя"
            }, status=status.HTTP_400_BAD_REQUEST)

        if Follow.objects.filter(user=request.user,
                                 author=author).exists():
            return Response({
                'errors': "Нельзя подписаться дважды"
            }, status=status.HTTP_400_BAD_REQUEST)

        follow = Follow.objects.create(
            user=request.user, author=author
        )
        serializer = FollowSerializer(
            follow, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        """Функции отписки от автора."""

        author = get_object_or_404(User, pk=id)

        if request.user == author:
            return Response({
                'errors': "Нельзя отписаться от самого себя"
            }, status=status.HTTP_400_BAD_REQUEST)

        subscribe = Follow.objects.filter(user=request.user, author=author)

        if not subscribe.exists():
            return Response({
                'errors': "Вы не были подписаны на этого пользователя"
            }, status=status.HTTP_400_BAD_REQUEST)
        subscribe.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated], url_path='subscriptions')
    def subscriptions(self, request):
        subscriptions = Follow.objects.filter(user=request.user)
        page = self.paginate_queryset(subscriptions)
        serializer = FollowSerializer(page, many=True,
                                      context={'request': request})

        return self.get_paginated_response(serializer.data)


class RecipeViewSet(ModelViewSet):
    """
    Вьюсет обработки моделей рецептов.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet
    pagination_class = PagePaginator
    permission_classes = (IsAuthorOrAdminOrReadOnly, IsAuthenticatedOrReadOnly)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    @staticmethod
    def post_method_for_actions(request, pk, serializers):
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        serializer = serializers(data=data, context={
            'request': request
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_method_for_actions(request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        model_instance = get_object_or_404(model, user=user, recipe=recipe)
        model_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post'],
        detail=True
    )
    def shopping_cart(self, request, pk):
        return self.post_method_for_actions(
            request, pk, serializers=ShoppingCartSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=ShoppingCart)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        cart = IngredientRecipe.objects.filter(
            recipe__cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            Sum('amount')
        )
        cart_txt = []
        for item in cart:
            cart_txt.append(
                item['ingredient__name'] + ' - '
                + str(item['amount__sum']) + ' '
                + item['ingredient__measurement_unit']
            )
        return generate_pdf(cart_txt)

    @action(
        methods=['post'],
        detail=True
    )
    def favorite(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=FavoriteSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=Favorite)


class IngredientViewSet(ModelViewSet):
    """
    Вьюсет обработки модели продуктов.
    """
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilter,)
    pagination_class = None
    search_fields = ('^name',)


class TagViewSet(ModelViewSet):
    """
    Вьюсет обработки моделей тегов.
    Добавить тег может администратор.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
