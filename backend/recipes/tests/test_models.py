import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import User


@pytest.mark.django_db
def test_tag_creation_and_str():
    tag = Tag.objects.create(name='Vegan', slug='vegan')
    assert str(tag) == 'Vegan'


@pytest.mark.django_db
def test_ingredient_creation_and_unique_constraint():
    ing1 = Ingredient.objects.create(name='Tomato', measurement_unit='pcs')
    assert str(ing1) == 'Tomato'
    with pytest.raises(IntegrityError):
        Ingredient.objects.create(name='Tomato', measurement_unit='pcs')


@pytest.mark.django_db
def test_recipe_creation_and_str():
    user = User.objects.create_user(
        email='chef@example.com',
        username='chef',
        first_name='Chef',
        last_name='Cook',
        password='12345'
    )
    image = SimpleUploadedFile('dish.jpg',
                               b'image-data', content_type='image/jpeg')
    recipe = Recipe.objects.create(
        author=user,
        name='Pasta',
        text='Boil pasta and serve',
        cooking_time=10,
        image=image
    )
    assert str(recipe) == 'Pasta'


@pytest.mark.django_db
def test_recipe_minimum_cooking_time():
    user = User.objects.create_user(
        email='test@example.com',
        username='testuser',
        first_name='Test',
        last_name='User',
        password='12345'
    )
    image = SimpleUploadedFile('r.jpg', b'image', content_type='image/jpeg')
    with pytest.raises(ValidationError):
        recipe = Recipe(
            author=user,
            name='Bad Dish',
            text='Too fast',
            cooking_time=0,
            image=image
        )
        recipe.full_clean()


@pytest.mark.django_db
def test_recipe_ingredient_unique_constraint():
    ing = Ingredient.objects.create(name='Salt', measurement_unit='g')
    user = User.objects.create_user(
        email='r@example.com',
        username='rr',
        first_name='R',
        last_name='R',
        password='12345'
    )
    image = SimpleUploadedFile('dish.jpg', b'data', content_type='image/jpeg')
    recipe = Recipe.objects.create(
        author=user,
        name='Soup',
        text='Make soup',
        cooking_time=15,
        image=image
    )
    RecipeIngredient.objects.create(recipe=recipe, ingredient=ing, amount=1)
    with pytest.raises(IntegrityError):
        RecipeIngredient.objects.create(recipe=recipe,
                                        ingredient=ing, amount=2)


@pytest.mark.django_db
def test_favorite_unique_constraint_and_str():
    user = User.objects.create_user(
        email='fav@example.com',
        username='fav',
        first_name='Fav',
        last_name='User',
        password='12345'
    )
    image = SimpleUploadedFile('img.jpg', b'data', content_type='image/jpeg')
    recipe = Recipe.objects.create(
        author=user,
        name='Burger',
        text='Fry and eat',
        cooking_time=5,
        image=image
    )
    fav = Favorite.objects.create(user=user, recipe=recipe)
    assert str(fav) == 'fav favorited Burger'
    with pytest.raises(IntegrityError):
        Favorite.objects.create(user=user, recipe=recipe)


@pytest.mark.django_db
def test_shopping_cart_unique_constraint_and_str():
    user = User.objects.create_user(
        email='cart@example.com',
        username='cartuser',
        first_name='Cart',
        last_name='User',
        password='12345'
    )
    image = SimpleUploadedFile('img.jpg', b'data', content_type='image/jpeg')
    recipe = Recipe.objects.create(
        author=user,
        name='Cake',
        text='Bake it',
        cooking_time=30,
        image=image
    )
    cart = ShoppingCart.objects.create(user=user, recipe=recipe)
    assert str(cart) == "Cake in cartuser's cart"
    with pytest.raises(IntegrityError):
        ShoppingCart.objects.create(user=user, recipe=recipe)
