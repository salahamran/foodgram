import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser', email='test@example.com', password='pass1234'
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def tag():
    return Tag.objects.create(
        name='Завтрак', slug='breakfast', color='#E26C2D')


@pytest.fixture
def ingredient():
    return Ingredient.objects.create(name='соль', measurement_unit='г')


@pytest.fixture
def recipe(user, tag, ingredient):
    recipe = Recipe.objects.create(
        author=user,
        name='Омлет',
        text='Взбить яйца и жарить',
        cooking_time=10
    )
    recipe.tags.add(tag)
    RecipeIngredient.objects.create(
        recipe=recipe, ingredient=ingredient, amount=1)
    return recipe
