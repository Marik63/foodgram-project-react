﻿from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import IngredientSearchFilter, RecipeFilterSet
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
from users.models import Follow, User


class CustomUserViewSet(UserViewSet):
    """
    Кастомный юзер вьюсет.
    """
    pagination_class = PagePaginator

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        methods=['get'],
        detail=False
    )
    def subscriptions(self, request):
        subscriptions_list = self.paginate_queryset(
            User.objects.filter(following__user=request.user)
        )
        serializer = FollowListSerializer(
            subscriptions_list,
            many=True,
            context={
                'request': request
            }
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True
    )
    def subscribe(self, request, id):
        if request.method != 'POST':
            subscription = get_object_or_404(
                Follow,
                author=get_object_or_404(User, id=id),
                user=request.user
            )
            self.perform_destroy(subscription)
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = FollowSerializer(
            data={
                'user': request.user.id,
                'author': get_object_or_404(User, id=id).id
            },
            context={
                'request': request
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RecipeViewSet(ModelViewSet):
    """
    Вьюсет обработки моделей рецептов.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PagePaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        if self.action == 'favorite':
            return FavoriteSerializer
        if self.action == 'shopping_cart':
            return ShoppingCartSerializer
        return CreateRecipeSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            self.permission_classes = (AllowAny,)
        elif self.action in ('favorite', 'shopping_cart'):
            self.permission_classes = (IsAuthenticated,)
        elif self.request.method in (
            'PATCH', 'DELETE'
        ):
            self.permission_classes = (IsAuthorOrAdminOrReadOnly,)
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['get'], detail=False,
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
        methods=['post', 'delete'], detail=True,
    )
    def favorite(self, request, pk):
        func_model = Favorite
        return custom_post_delete(self, request, pk, func_model)

    @action(
        methods=['post', 'delete'], detail=True,
    )
    def shopping_cart(self, request, pk):
        func_model = ShoppingCart
        return custom_post_delete(self, request, pk, func_model)


def custom_post_delete(self, request, pk, func_model):
    """
    Обработка delete, post запросов.
    """

    user = self.request.user
    recipe = self.get_object()
    if request.method == 'DELETE':
        instance = func_model.objects.filter(recipe=recipe, user=user)
        if not instance:
            raise serializers.ValidationError(
                {
                    'errors': [
                        'Этот рецепт в списке отсутствует.'
                    ]
                }
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    data = {
        'user': user.id,
        'recipe': pk
    }
    favorite = self.get_serializer(data=data)
    favorite.is_valid(raise_exception=True)
    favorite.save()
    serializer = ShoppingCartSerializer(recipe)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class IngredientViewSet(ModelViewSet):
    """
    Вьюсет обработки модели продуктов.
    """
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
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
