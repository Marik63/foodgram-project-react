from django_filters import rest_framework as filter
from rest_framework import filters

from recipes.models import Recipe


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'


class RecipeFilterSet(filter.FilterSet):
    tags = filter.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = filter.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filter.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags',
                  'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(in_favorite__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(cart__user=self.request.user)
        return queryset.all()
