import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_recipe_detail_route(api_client, recipe):
    url = reverse('recipes-detail', kwargs={'id': recipe.id})
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['id'] == recipe.id


@pytest.mark.django_db
def test_download_cart(auth_client):
    url = reverse('recipes-download-shopping-cart')
    response = auth_client.get(url)
    assert response.status_code == 200
    assert 'Shopping List' in response.content.decode()
