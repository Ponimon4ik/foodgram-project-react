from rest_framework import status, permissions, mixins, viewsets, pagination, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core import serializers

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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user, patrial=True)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated, ),
        serializer_class=FavoriteRecipeWriteSerializer
    )
    def favorite(self, request, pk=None):
        if request.method == 'DELETE':
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        serializer = FavoriteRecipeWriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListRetrieveViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, viewsets.GenericViewSet
):

    permission_classes = (permissions.AllowAny, )

    pass


class TagViewSet(ListRetrieveViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ListRetrieveViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class APIFavoriteRecipe(views.APIView):

    lookup_field = 'recipe'

    # def post(self, request):
    #     recipe = Recipe.objects.get(id=self.kwargs.get('recipe'))
    #     data = {
    #         'user': request.user,
    #         'recipe': recipe
    #     }
    #     serializer = FavoriteRecipeWriteSerializer(data=data)
    #     serializer.is_valid(raise_exception=True)
    #     validate_data = serializer.validated_data
    #     FavoriteRecipe.objects.create(**validate_data)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

