import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_invalid_ingredient(auth_client, tag):
    url = reverse('recipes-list')
    data = {
        'name': 'Рецепт без ингредиентов',
        'text': 'Описание',
        'cooking_time': 10,
        'ingredients': [{'id': 999, 'amount': 5}],
        'tags': [tag.id],
        'image': (
            'data:image/png;base64,'
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywa'
            'AAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4b'
            'AAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=='
        ),

    }
    response = auth_client.post(url, data, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_recipe_with_zero_amount(auth_client, ingredient, tag):
    url = reverse('recipes-list')
    data = {
        'name': 'Ноль ингредиентов',
        'text': 'Попытка',
        'cooking_time': 5,
        'ingredients': [{'id': ingredient.id, 'amount': 0}],
        'tags': [tag.id],
        'image': (
            'data:image/png;base64,'
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywa'
            'AAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4b'
            'AAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=='
        )
    }
    response = auth_client.post(url, data, format='json')
    assert response.status_code == 400
