from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Tag(models.Model):
    """
    Модель тегов.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Название тега',
        help_text='Введите название тега',
        db_index=True
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='Slug',
        help_text='Введите текстовый идентификатор тега',
        unique=True
    )
    color = ColorField(
        format='hex',
        verbose_name='Цвет',
        max_length=7,
        help_text='Введите цвет тега')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    """
    Модель ингридиентов.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',
        help_text='Введите название продуктов',
        null=False,
        db_index=True
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
        help_text='Введите единицы измерения',
        null=False
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """
    Модель рецептов.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes',
        help_text='Выберите автора рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты',
        related_name='recipes',
        help_text='Выберите продукты рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        help_text='Добавить дату создания',
        auto_now_add=True
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Введите описания рецепта',
        max_length=500
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
        help_text='Введите название рецепта',
        null=False
    )
    image = models.ImageField(
        null=True,
        upload_to='recipes/images/',
        verbose_name='Изображение',
        help_text='Выберите изображение рецепта',
        default=None
    )
    cooking_time = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1, 'Значение не может быть меньше 1')],
        verbose_name='Время готовки в минутах',
        help_text='Введите время приготовления'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'Автор: {self.author.username} рецепт: {self.name}'


class Favorite(models.Model):
    """
    Модель избранных рецептов.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='in_favorite',
        help_text='Выберите пользователя'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        default_related_name = 'favorites'
        UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_favorites')

    def __str__(self):
        return f"{self.user} избран {self.recipe.name}"


class ShoppingCart(models.Model):
    """
    Модель списка покупок.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользоавтель',
        help_text='Выберите пользователя',
        related_name='cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        help_text='Выберите рецепты для добавления в корзины',
        related_name='cart',
    )
    added = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления в список покупок'
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_cart')

    def __str__(self):
        return (f'Пользователь: {self.user.username},'
                f'рецепт в списке: {self.recipe.name}')


class IngredientRecipe(models.Model):
    """
    Кастомная модель свяизи ингридиентов и рецептов.
    """
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        help_text='Добавить продукты рецепта в корзину'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите рецепт'
    )
    amount = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Количество ингредиентов',
        help_text='Введите количество продукта'
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        default_related_name = 'ingridients_recipe'
        UniqueConstraint(
            fields=['ingredient', 'recipe'],
            name='unique_ingredient')

    def __str__(self):
        return (f'В рецепте {self.recipe.name} {self.amount} '
                f'{self.ingredient.measurement_unit} {self.ingredient.name}')


class TagRecipe(models.Model):
    """
    Кастомная модель связи тэгов и рецепта.
    """
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name='Теги',
        help_text='Выберите теги рецепта'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите рецепт')

    class Meta:
        verbose_name = 'Теги рецепта'
        verbose_name_plural = 'Теги рецепта'
        UniqueConstraint(
            fields=['tag', 'recipe'],
            name='unique_tagrecipe')

    def __str__(self):
        return f'{self.tag} {self.recipe}'
