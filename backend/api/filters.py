from django_filters import rest_framework as filters
from recipes.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    """Filter recipes by tags, author, is_favorited, is_in_shopping_cart."""

    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='Filter by tag slug'
    )
    author = filters.NumberFilter(
        field_name='author__id',
        label='Filter by author ID'
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shoppingcart__user=self.request.user)
        return queryset
