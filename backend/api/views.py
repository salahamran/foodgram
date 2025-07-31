import json

from api.filters import RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeShortSerializer,
    RecipeWriteSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserSerializer,
)
from django.db.models import F, Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Subscription, User


class UserViewSet(viewsets.ModelViewSet):
    """Handle the user views and subscriptions."""

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['subscriptions', 'subscribe']:
            return SubscriptionSerializer
        return UserSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        user = request.user

        if user.id == author.id:
            return Response(
                {"errors": "You cannot subscribe to yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {"errors": "Already subscribed"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Subscription.objects.create(user=user, author=author)
            context = {'request': request}
            recipes_limit = request.query_params.get('recipes_limit')
            if recipes_limit and recipes_limit.isdigit():
                context['recipes_limit'] = int(recipes_limit)
            serializer = SubscriptionSerializer(author, context=context)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE
        subscription = Subscription.objects.filter(user=user, author=author)
        if not subscription.exists():
            return Response(
                {"errors": "Subscription not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        authors = User.objects.filter(followers__user=user)

        context = {'request': request}
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit and recipes_limit.isdigit():
            context['recipes_limit'] = int(recipes_limit)

        page = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(page, many=True, context=context)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(
            request.user, context={'request': request})
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """Main logic for recipes: CRUD, favorites, cart, download."""

    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        if 'ingredients' in data and isinstance(data['ingredients'], str):
            try:
                data['ingredients'] = json.loads(data['ingredients'])
            except json.JSONDecodeError:
                return Response(
                    {"ingredients": ["Invalid format"]},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if 'tags' in data and isinstance(data['tags'], str):
            try:
                data['tags'] = json.loads(data['tags'])
            except json.JSONDecodeError:
                return Response(
                    {"tags": ["Invalid format"]},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        read_serializer = RecipeReadSerializer(serializer.instance,
                                               context={'request': request})
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"detail": "Recipe not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def get_queryset(self):
        queryset = super().get_queryset()

        author_id = self.request.query_params.get('author')
        tags = self.request.query_params.getlist('tags')
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        limit = self.request.query_params.get('limit')

        if author_id:
            queryset = queryset.filter(author__id=author_id)

        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        if is_favorited and self.request.user.is_authenticated:
            queryset = queryset.filter(favorite__user=self.request.user)

        if is_in_shopping_cart and self.request.user.is_authenticated:
            queryset = queryset.filter(shoppingcart__user=self.request.user)

        if limit and limit.isdigit():
            queryset = queryset[:int(limit)]

        return queryset

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, id=None):
        recipe = get_object_or_404(Recipe, id=id)
        user = request.user

        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'error': 'Already favorited.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            favorite = Favorite.objects.filter(user=user, recipe=recipe)
            if not favorite.exists():
                return Response(
                    {'error': 'Not in favorites.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='shopping_cart', url_name='shopping_cart')
    def shopping_cart(self, request, id=None):
        recipe = get_object_or_404(Recipe, id=id)
        user = request.user

        if request.method == 'POST':
            if Favorite.objects.filter(user=request.user,
                                       recipe=recipe).exists():
                return Response(
                    {"errors": "Already in favorites."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        item = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if not item.exists():
            return Response(
                {'errors': 'Not in shopping cart.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = (
            ShoppingCart.objects
            .filter(user=request.user)
            .values(
                name=F('recipe__ingredients__name'),
                unit=F('recipe__ingredients__measurement_unit')
            )
            .annotate(total_amount=Sum('recipe__recipe_ingredient__amount'))
            .order_by('name')
        )

        content = "Shopping List:\n\n"
        for i, item in enumerate(ingredients, 1):
            content += (
                f"{i}. {item['name']} "
                f"({item['unit']}) - "
                f"{item['total_amount']}\n"
            )
        response = HttpResponse(content, content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        data = request.data.copy()
        if 'ingredients' in data and isinstance(data['ingredients'], str):
            try:
                data['ingredients'] = json.loads(data['ingredients'])
            except json.JSONDecodeError:
                return Response(
                    {"ingredients": ["Invalid format"]},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if 'tags' in data and isinstance(data['tags'], str):
            try:
                data['tags'] = json.loads(data['tags'])
            except json.JSONDecodeError:
                return Response(
                    {"tags": ["Invalid format"]},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        read_serializer = RecipeReadSerializer(
            serializer.instance, context={'request': request})
        return Response(read_serializer.data)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, id=None):
        recipe = self.get_object()
        return Response({
            'short-link': f'/api/recipes/{recipe.id}/download/'
        })


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Manage tags for recipes (list/retrieve only)."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    lookup_field = 'id'


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ingredient viewset with search."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class AvatarUpdateView(APIView):
    """Viewset for updating the Avatar."""

    permission_classes = [IsAuthenticated]

    def put(self, request):
        if 'avatar' not in request.data:
            return Response(
                {"avatar": ["This field is required"]},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AvatarSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "No avatar to delete"},
            status=status.HTTP_400_BAD_REQUEST
        )


class SetPasswordView(APIView):
    """Viewset for overriding the pass model."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
