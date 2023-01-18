from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    SAFE_METHODS, AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import RecipeFilterSet
from .paginator import PagePaginator
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (CreateRecipeSerializer,
                          FavoriteSerializer, FollowListSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer)
from .utils import generate_pdf

from recipes.models import (Favorite, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import User


class CustomUserViewSet(UserViewSet):
    """
    Кастомный юзер вьюсет.
    """
    pagination_class = PagePaginator

    @action(
        methods=['get'], detail=False,
        serializer_class=FollowListSerializer
    )
    def subscriptions(self, request):
        user = self.request.user

        def queryset():
            return User.objects.filter(following__user=user)

        self.get_queryset = queryset
        return self.list(request)

    @action(
        methods=['post', 'delete'], detail=True,
        serializer_class=FollowSerializer
    )
    def subscribe(self, request, id):
        user = self.request.user
        following = self.get_object()
        if request.method == 'DELETE':
            instance = user.follower.filter(following=following)
            if not instance:
                raise serializers.ValidationError(
                    {
                        'errors': [
                            'Вы не подписаны на этого автора.'
                        ]
                    }
                )
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        data = {
            'user': user.id,
            'following': id
        }
        subscription = FollowSerializer(data=data)
        subscription.is_valid(raise_exception=True)
        subscription.save()
        serializer = self.get_serializer(following)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
