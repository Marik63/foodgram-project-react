from django.conf import settings
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField,
                                        ValidationError)
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import Follow, User


class UsersSerializer(UserSerializer):
    """
    Класс сериализатора для управления пользователями.
    """
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj: User):
        """
        Функция определения подписан ли текущий пользователь на автора.
        """
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj
        ).exists()


class UserCreateSerializer(UserCreateSerializer):
    """
    Класс сериализатора для создание пользователя.
    """

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'role'
        )

    def validate_username(self, data):
        if User.objects.filter(username=data).exists():
            raise ValidationError(
                "Пользователь уже зарегестрирован."
            )
        return data

    def validate_email(self, data):
        if User.objects.filter(email=data).exists():
            raise ValidationError(
                "Email уже зарегестрировано."
            )
        return data


class FollowListSerializer(ModelSerializer):
    """
    Класс сериализатора списка на кого подписан пользователь.
    """
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()

    def get_recipes(self, author):
        queryset = self.context.get('request')
        recipes_limit = queryset.query_params.get('recipes_limit')
        if not recipes_limit:
            return RecipeShortInfo(
                Recipe.objects.filter(author=author),
                many=True, context={
                    'request': queryset
                }
            ).data
        return RecipeShortInfo(
            Recipe.objects.filter(author=author)[:int(recipes_limit)],
            many=True,
            context={
                'request': queryset
            }
        ).data

    def get_is_subscribed(self, author):
        return Follow.objects.filter(
            user=self.context.get('request').user,
            author=author
        ).exists()


class FollowSerializer(ModelSerializer):
    """
    Класс сериализатора для управления подписками.
    """
    class Meta:
        model = Follow
        fields = ('user', 'author')

        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='На этого пользователя Вы уже подписаны!'
            )
        ]

    def validate(self, data):
        get_object_or_404(User, username=data['author'])
        if self.context['request'].user == data['author']:
            raise ValidationError({
                'errors': 'Ты не пожешь подписаться сам на себя.'
            })
        return data

    def to_representation(self, instance):
        return FollowListSerializer(
            instance.author,
            context={
                'request': self.context.get('request')
            }
        ).data


class FavoriteOrCartSerializer(ModelSerializer):
    """
    Отображение рецептов в избранном, списке покупок.
    """

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = (
            'name',
            'image',
            'cooking_time'
        )


class TagSerializer(ModelSerializer):
    """
    Сериализатор для тегов.
    """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):
    """
    Сериализатор для ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsRecipesSaveSerializator(serializers.Serializer):
    """
    Сериализатор для сохранения ингридентов рецепта.
    """

    id = IntegerField()
    amount = IntegerField(min_value=settings.MIN_PRODUCT)


class IngredientRecipeSerializer(ModelSerializer):
    id = IntegerField(
        source='ingredient',
        read_only=True
    )
    name = serializers.CharField(
        source='ingredient',
        read_only=True
    )
    measurement_unit = serializers.RelatedField(
        source='ingredient',
        read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id', 'name',
            'measurement_unit', 'amount'
        )


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        read_only=True,
        source='ingridients_recipe',
    )
    author = UsersSerializer(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    is_favorited = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user,
            recipe__id=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe__id=obj.id
        ).exists()


class CreateIngredientRecipeSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')

    def validate_amount(self, data):
        if int(data) < 1:
            raise ValidationError({
                'ingredients': (
                    'Количество должно быть больше 1'
                ),
                'msg': data
            })
        return data

    def create(self, validated_data):
        return IngredientRecipe.objects.create(
            ingredient=validated_data.get('id'),
            amount=validated_data.get('amount')
        )


class CreateRecipeSerializer(ModelSerializer):
    author = UsersSerializer(read_only=True)
    image = Base64ImageField(use_url=True, max_length=None)
    ingredients = CreateIngredientRecipeSerializer(many=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    cooking_time = IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'image', 'tags', 'author',
            'ingredients', 'name', 'text', 'cooking_time'
        )

    def create_ingredients(self, recipe, ingredients):
        IngredientRecipe.objects.bulk_create([
            IngredientRecipe(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=ingredient['ingredient'],
            ) for ingredient in ingredients
        ])

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise ValidationError(
                    'Есть повторяющиеся ингредиенты!'
                )
            ingredients_list.append(ingredient_id)
        if data['cooking_time'] <= 0:
            raise ValidationError(
                'Время приготовления не должно быть 0.'
            )
        return data

    @atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=request.user,
            **validated_data
        )
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = instance
        IngredientRecipe.objects.filter(recipe=recipe).delete()
        self.create_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request'),
            }
        ).data


class RecipeShortInfo(ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id', 'name',
            'image', 'cooking_time'
        )


class FavoriteSerializer(ModelSerializer):
    """
    Добавление рецепта в избранное.
    """

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            raise ValidationError({
                'errors': 'Этот рецепт уже добавлен в избранное!'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {
            'request': request
        }
        return RecipeShortInfo(
            instance.recipe,
            context=context
        ).data


class ShoppingCartSerializer(ModelSerializer):
    """
    Добавление рецепта в список покупок.
    """

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')

    def validate(self, data):
        user = self.context.get('request').user
        recipe = data['recipe']
        if ShoppingCart.objects.filter(
            user=user,
            recipe=recipe
        ).exists():
            raise ValidationError({
                'errors': 'Рецепт уже добавлен в список покупок!'})
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {
            'request': request
        }
        return RecipeShortInfo(
            instance.recipe,
            context=context
        ).data
