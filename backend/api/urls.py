from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    AvatarUpdateView,
    IngredientViewSet,
    RecipeViewSet,
    SetPasswordView,
    TagViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    path("users/set_password/", SetPasswordView.as_view(),
         name="set_password"),
    path("users/me/avatar/", AvatarUpdateView.as_view(),
         name="users-avatar"),
    path("", include(router.urls)),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
