from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'slug')
    list_display_links = ('name', 'id')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'measurement_unit')
    list_display_links = ('name', 'id')
    search_fields = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'author', 'cooking_time')
    list_display_links = ('name', 'id', 'author')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    inlines = [RecipeIngredientInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('author').prefetch_related(
            'tags',
            'recipe_ingredients__ingredient'
        )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'user',
            'recipe',
            'recipe__author',
        ).prefetch_related(
            'recipe__tags',
            'recipe__recipe_ingredients__ingredient',
        )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'user',
            'recipe',
            'recipe__author',
        ).prefetch_related(
            'recipe__tags',
            'recipe__recipe_ingredients__ingredient',
        )
