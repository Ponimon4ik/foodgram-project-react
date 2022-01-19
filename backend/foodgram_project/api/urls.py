from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, TagViewSet, IngredientViewSet, APIFavoriteRecipe

FAVORITE_RECIPE_URL = r'recipes/(?P<recipe_id>\d+)/favorite/'

router_v1 = DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='user')
router_v1.register('tags', TagViewSet, basename='tag')
router_v1.register('ingredients', IngredientViewSet, basename='ingredient')


urlpatterns = [
    path('v1/', include('users.urls')),
    path('v1/', include(router_v1.urls)),
    path(r'v1/recipes/(?P<recipe_id>\d+)/favorite/', APIFavoriteRecipe.as_view())
]
