from rest_framework import (status, viewsets, pagination)
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from recipes.models import (Recipe, Tag, Ingredient,
                            FavoriteRecipe, ShoppingCart)
from .serializers import (RecipeReadSerializer, RecipeWriteSerializer,
                          TagSerializer, IngredientSerializer,
                          FavoriteRecipeWriteSerializer,
                          ShoppingCartSerializer)
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
        detail=True
    )
    def favorite(self, request, pk=None):
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        if request.method == 'DELETE':
            if FavoriteRecipe.objects.filter(**data).exists():
                favorite_recipe = get_object_or_404(FavoriteRecipe, **data)
                self.perform_destroy(favorite_recipe)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепт не был в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        get_object_or_404(Recipe, pk=pk)
        serializer = FavoriteRecipeWriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['post', 'delete'],
        detail=True,
    )
    def shopping_cart(self, request, pk=None):
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        if request.method == 'DELETE':
            if ShoppingCart.objects.filter(**data).exists():
                shoping_list_recipe = get_object_or_404(ShoppingCart, **data)
                self.perform_destroy(shoping_list_recipe)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепт не был в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        get_object_or_404(Recipe, pk=pk)
        serializer = ShoppingCartSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
