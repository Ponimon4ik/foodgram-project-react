from rest_framework import (status, permissions,
                            viewsets, pagination)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from recipes.models import Recipe, Tag, Ingredient, FavoriteRecipe
from .serializers import (RecipeReadSerializer, RecipeWriteSerializer,
                          TagSerializer, IngredientSerializer,
                          FavoriteRecipeWriteSerializer)
from .permissions import IsAuthorOrAdminOrReadOnly


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (IsAuthorOrAdminOrReadOnly, )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated, ),
        serializer_class=FavoriteRecipeWriteSerializer
    )
    def favorite(self, request, pk=None):
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        if request.method == 'DELETE':
            favorite_recipe = get_object_or_404(FavoriteRecipe, **data)
            self.perform_destroy(favorite_recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = FavoriteRecipeWriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
