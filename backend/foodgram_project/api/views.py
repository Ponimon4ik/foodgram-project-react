from rest_framework import status, permissions, mixins, viewsets, pagination
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Recipe, TagRecipe, Tag, Ingredient, IngredientRecipe
from .serializers import RecipeReadSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (permissions.AllowAny, )
    serializer_class = RecipeReadSerializer
