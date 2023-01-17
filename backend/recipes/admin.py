from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe,
                     Recipe, ShoppingCart, Tag, TagRecipe)


class IngredientAdmin(admin.ModelAdmin):
    """
    Параметры админ панели (управление ингредиентами).
    """
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', )
    empty_value_display = '-пусто-'
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    """
    Параметры админ панели (управление тегами).
    """
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', )
    empty_value_display = '-пусто-'
    list_filter = ('name',)


class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Параметры админ зоны продуктовой корзины.
    """
    list_display = ('user', 'recipe')
    search_fields = ('user', )
    empty_value_display = '-пусто-'
    list_filter = ('user', 'recipe')


class FavoriteAdmin(admin.ModelAdmin):
    """
    Параметры админ зоны избранных рецептов.
    """
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = '-пусто-'
    list_filter = ('user', 'recipe')


class RecipeAdmin(admin.ModelAdmin):
    """
    Параметры админ панели (управление рецептами).
    """
    list_display = ('author', 'name', 'in_favorite')
    search_fields = ('name')
    empty_value_display = '-пусто-'
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('tags',)
    readonly_fields = ('in_favorite',)

    def in_favorite(self, obj):
        """
        Метод для подсчета общего числа
        добавлений этого рецепта в избранное.
        """
        return obj.in_favorite.all().count()
    in_favorite.short_description = 'Число добавлении в избранное'


admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientRecipe)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(TagRecipe)
