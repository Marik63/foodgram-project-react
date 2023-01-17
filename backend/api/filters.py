from django_filters import rest_framework as django_filter

from recipes.models import Recipe, Tag


class RecipeFilterSet(django_filter.FilterSet):
    """
    Класс фильтр  для рецептов.
    """

    tags = django_filter.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug'
    )
    is_favorited = django_filter.NumberFilter(
        method='get_is_favorited',
        field_name='favorite__user'
    )
    is_in_shopping_cart = django_filter.NumberFilter(
        method='get_is_in_shopping_cart',
        field_name='cart__user'
    )

    class Meta:
        model = Recipe
        fields = ('author')

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated or not int(value):
            return queryset.filter(in_favorite__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated or not int(value):
            return queryset.filter(cart__user=self.request.user)
        return queryset.all()
