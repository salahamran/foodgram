import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_get_recipe_list(api_client, recipe):
    url = reverse('recipes-list')
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['count'] >= 1


@pytest.mark.django_db
def test_create_recipe(auth_client, tag, ingredient):
    url = reverse('recipes-list')
    data = {
        'name': 'Новый рецепт',
        'text': 'Описание рецепта',
        'cooking_time': 5,
        'ingredients': [{'id': ingredient.id, 'amount': 10}],
        'tags': [tag.id],
        'image': (
            'data:image/png;base64,'
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywa'
            'AAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4b'
            'AAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=='
        ),
    }
    response = auth_client.post(url, data, format='json')
    assert response.status_code == 201
    assert response.data['name'] == 'Новый рецепт'
