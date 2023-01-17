from django_filters import rest_framework as django_filter
from rest_framework import filters

from recipes.models import Recipe


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'


class RecipeFilterSet(django_filter.FilterSet):
    tags = django_filter.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = django_filter.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = django_filter.BooleanFilter(
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
