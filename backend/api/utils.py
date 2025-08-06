def get_is_favorited(recipe, user):
    """Check if the recipe is favorited by the current user."""
    if user.is_anonymous:
        return False
    return recipe.favorited_by.filter(user=user).exists()


def get_is_in_shopping_cart(recipe, user):
    """Check if the recipe is in the current user's shopping cart."""
    if user.is_anonymous:
        return False
    return recipe.in_shopping_carts.filter(user=user).exists()
