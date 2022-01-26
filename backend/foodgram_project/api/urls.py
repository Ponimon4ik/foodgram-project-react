from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

FAVORITE_RECIPE_URL = r'recipes/(?P<recipe_id>\d+)/favorite/'

router_v1 = DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='user')
router_v1.register('tags', TagViewSet, basename='tag')
router_v1.register('ingredients', IngredientViewSet, basename='ingredient')


urlpatterns = [
    path('', include('users.urls')),
    path('', include(router_v1.urls)),
]
