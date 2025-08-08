from django.db.models import Count, F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartSerializer,
    SubscriptionCreateSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserSerializer,
)
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
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

        if request.method == 'POST':
            serializer = SubscriptionCreateSerializer(
                data={'author': author.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted_count, _ = Subscription.objects.filter(
            user=user,
            author_id=id
        ).delete()

        if deleted_count == 0:
            return Response(
                {'errors': 'Not subscribed to this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        recipes_limit = request.query_params.get('recipes_limit')
        context = {'request': request}
        if recipes_limit and recipes_limit.isdigit():
            context['recipes_limit'] = int(recipes_limit)

        authors = User.objects.filter(
            followers__user=user
        ).annotate(
            recipes_count=Count('recipes')
        )

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

    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'recipe_ingredients__ingredient'
    )
    permission_classes = [IsAuthorOrReadOnly]
    serializer_class = RecipeReadSerializer
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        read_serializer = RecipeReadSerializer(
            serializer.instance, context={'request': request})
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        read_serializer = RecipeReadSerializer(
            serializer.instance, context={'request': request})
        return Response(read_serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='favorite')
    def favorite(self, request, id=None):
        recipe = get_object_or_404(Recipe, id=id)

        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'recipe': recipe.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted_count, _ = Favorite.objects.filter(
            user=request.user,
            recipe_id=id
        ).delete()

        if deleted_count == 0:
            return Response(
                {'errors': 'Not in favorites.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='shopping_cart')
    def shopping_cart(self, request, id=None):
        recipe = get_object_or_404(Recipe, id=id)

        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={'recipe': recipe.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted_count, _ = ShoppingCart.objects.filter(
            user=request.user,
            recipe_id=id
        ).delete()

        if deleted_count == 0:
            return Response(
                {'errors': 'Not in shopping cart.'},
                status=status.HTTP_400_BAD_REQUEST
            )
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
            .annotate(total_amount=Sum('recipe__recipe_ingredients__amount'))
            .order_by('name')
        )

        content = self._generate_shopping_list_content(ingredients)
        response = HttpResponse(content, content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response

    def _generate_shopping_list_content(self, ingredients):
        content = 'Shopping List:\n\n'
        for i, item in enumerate(ingredients, 1):
            content += (
                f'{i}. {item["name"]} '
                f'({item["unit"]}) - '
                f'{item["total_amount"]}\n'
            )
        return content

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, id=None):
        recipe = self.get_object()
        return Response({
            'short-link': f'/api/recipes/{recipe.id}/'
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class AvatarUpdateView(APIView):
    """Viewset for updating the Avatar."""

    permission_classes = [IsAuthenticated]

    def put(self, request):
        if 'avatar' not in request.data:
            return Response(
                {'avatar': ['This field is required']},
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
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'No avatar to delete'},
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
