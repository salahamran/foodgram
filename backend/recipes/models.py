from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=256, unique=True, verbose_name='Tag Name')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=256, verbose_name='Ingredient Name')
    measurement_unit = models.CharField(
        max_length=256, verbose_name='Measurement Unit')

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        constraints = [models.UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='unique_ingredient'
        )]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Recipe Author')
    name = models.CharField(
        max_length=256, verbose_name='Recipe Name')
    image = models.ImageField(upload_to='recipes/images/', verbose_name='Image Field')
    text = models.TextField(verbose_name='Recipe Text')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Cooking time'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Tags')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ingredients')

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ['-id']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        null=True,
        related_name='recipe_ingredient',
        verbose_name='Recipe using Ingerdients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        null=True,
        related_name='ingredients_in_recipes',
        verbose_name='Ingredient'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Amount'
    )

    class Meta:
        verbose_name = 'Recipe Ingredient'
        verbose_name_plural = 'Recipes Ingredients'
        ordering = ['-id']
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='unique_recipe_ingredient'
        )]

    def __str__(self):
        return f'{self.ingredient.name} in {self.recipe.name}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='User favorites',
        related_name='favorite'

    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='user favorite recipe'
    )

    class Meta:
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorite'
        )]

    def __str__(self):
        return f'{self.user.username} favorited {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='User Product'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Recipe in Cart'
    )

    class Meta:
        verbose_name = 'Shopping Cart'
        verbose_name_plural = 'Shopping Carts'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_cart_item'
        )]

    def __str__(self):
        return f'{self.recipe.name} in {self.user.username}\'s cart'

