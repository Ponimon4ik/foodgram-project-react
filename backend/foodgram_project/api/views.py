from rest_framework import status, permissions, mixins, viewsets, pagination
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Recipe, TagRecipe, Tag, Ingredient, IngredientRecipe
from .serializers import RecipeReadSerializer, RecipeWriteSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (permissions.AllowAny, )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)