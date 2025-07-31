import pytest

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError

from users.models import Subscription, User


@pytest.mark.django_db
def test_user_creation_and_str():
    user = User.objects.create_user(
        email='test@example.com',
        username='testuser',
        first_name='Test',
        last_name='User',
        password='securepassword'
    )
    assert str(user) == 'test@example.com'
    assert user.username == 'testuser'
    assert user.first_name == 'Test'
    assert user.last_name == 'User'
    assert user.check_password('securepassword') is True


@pytest.mark.django_db
def test_avatar_upload():
    avatar = SimpleUploadedFile(
        name='test.jpg',
        content=b'image-data',
        content_type='image/jpeg'
    )
    user = User.objects.create_user(
        email='avatar@example.com',
        username='avataruser',
        first_name='Ava',
        last_name='Tar',
        password='avatarpass',
        avatar=avatar
    )
    assert user.avatar.name.startswith('avatars/test.jpg')


@pytest.mark.django_db
def test_username_regex_validation():
    with pytest.raises(ValidationError):
        user = User(
            email='bad@example.com',
            username='invalid username!',
            first_name='Bad',
            last_name='User'
        )
        user.full_clean()


@pytest.mark.django_db
def test_unique_subscription_constraint():
    user1 = User.objects.create_user(
        email='user1@example.com',
        username='user1',
        first_name='User',
        last_name='One',
        password='password1'
    )
    user2 = User.objects.create_user(
        email='user2@example.com',
        username='user2',
        first_name='User',
        last_name='Two',
        password='password2'
    )
    Subscription.objects.create(user=user1, author=user2)
    with pytest.raises(IntegrityError):
        Subscription.objects.create(user=user1, author=user2)


@pytest.mark.django_db
def test_subscription_str():
    user = User.objects.create_user(
        email='alice@example.com',
        username='alice',
        first_name='Alice',
        last_name='A',
        password='12345'
    )
    author = User.objects.create_user(
        email='bob@example.com',
        username='bob',
        first_name='Bob',
        last_name='B',
        password='12345'
    )
    subscription = Subscription.objects.create(user=user, author=author)
    assert str(subscription) == 'alice follows bob'
