from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.utils import get_is_favorited
from api.utils import get_is_in_shopping_cart
from recipes.models import Ingredient
from recipes.models import Recipe
from recipes.models import RecipeIngredient
from recipes.models import Tag
from users.models import Subscription
from users.models import User


class RecipeShortSerializer(serializers.ModelSerializer):
    """serializer for showing minimum rcipe in info subscriptions."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    username = serializers.CharField(
        max_length=150,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message='Enter a valid username.'
        )]
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        allow_blank=False,
        error_messages={
            "blank": "Password cannot be empty.",
            "min_length": "Password must be at least 8 characters long."
        },
        validators=[validate_password]
    )

    email = serializers.EmailField(max_length=254, required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'The username "me" is not allowed.'
            )
        return value

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {'username': 'Username already exists.'})

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': 'Email already exists.'})

        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for displaying user data, with subscription status."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'avatar', 'is_subscribed'
        )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError("Username 'me' is not allowed")
        return value

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(user=request.user,
                                           author=obj).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for showing the list of authors a user is subscribed to."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return RecipeShortSerializer(
            recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Serializer for read representation of tags."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for listing and retrieval of ingredients."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Serializer for reading the recipes."""

    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return ""

    def get_ingredients(self, obj):
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return [
            {
                'id': ri.ingredient.id,
                'name': ri.ingredient.name,
                'measurement_unit': ri.ingredient.measurement_unit,
                'amount': ri.amount
            }
            for ri in recipe_ingredients
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return get_is_favorited(obj, request.user if request else None)

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return get_is_in_shopping_cart(obj, request.user if request else None)


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/editing recipes (POST, PUT, PATCH)."""

    image = Base64ImageField()
    ingredients = serializers.ListField(
        child=serializers.DictField(), write_only=True,
        required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True,
        required=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'ingredients', 'name', 'image',
            'text', 'cooking_time'
        )

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                "At least one ingredient is required.")

        seen = set()
        invalid_ids = []
        for item in value:
            ing_id = item.get('id')
            amount = item.get('amount')

            if not Ingredient.objects.filter(id=ing_id).exists():
                invalid_ids.append(ing_id)

            if ing_id in seen:
                raise serializers.ValidationError(
                    "Duplicate ingredients are not allowed.")
            seen.add(ing_id)

            if not isinstance(amount, int) or amount < 1:
                raise serializers.ValidationError(
                    f"Amount for ingredient id {ing_id} must be a positive."
                )

        if invalid_ids:
            raise serializers.ValidationError(
                f"Invalid ingredient IDs: {invalid_ids}"
            )

        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError("At least one tag is required.")

        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "Duplicate tags are not allowed.")

        return value

    def create_ingredients(self, recipe, ingredients_data):
        for item in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=item['id'],
                amount=item['amount']
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags is not None:
            instance.tags.set(tags)

        if ingredients_data is not None:
            instance.recipe_ingredient.all().delete()
            self.create_ingredients(instance, ingredients_data)

        return instance

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError("This field may not be blank.")
        return value

    def validate(self, data):
        request = self.context.get('request')
        method = request.method if request else None

        if method in ['POST', 'PUT']:
            if 'ingredients' not in data:
                raise serializers.ValidationError({
                    'ingredients': ['This field is required.']
                })
            if 'tags' not in data:
                raise serializers.ValidationError({
                    'tags': ['This field is required.']
                })

        if method == 'PATCH':
            if 'ingredients' not in request.data:
                raise serializers.ValidationError({
                    'ingredients': ['This field is required.']
                })
            if 'tags' not in request.data:
                raise serializers.ValidationError({
                    'tags': ['This field is required.']
                })

        return data


class FavoriteSerializer(serializers.ModelSerializer):
    """Serialzer for adding/removing recipes to/from favorites."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serialzer for adding/removing recipes to/from shopping cart."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Serialzer to represent the ingredient.

    Plus amount in a specific recipe (from M2M through model).
    """

    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    id = serializers.ReadOnlyField(source='ingredient.id')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
