from rest_framework import status, permissions, mixins, viewsets, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core import serializers

from recipes.models import Recipe, TagRecipe, Tag, Ingredient, IngredientRecipe, User
from .serializers import RecipeReadSerializer, RecipeWriteSerializer, TagRecipeSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (permissions.AllowAny, )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    # def create(self, request, *args, **kwargs):
    #     serializer_recipe = self.get_serializer(data=request.data)
    #     serializer_recipe.is_valid(raise_exception=True)
    #     serializer_recipe.save(author=self.request.user)
    #     tag_list = []
    #     for tag_id in serializer_recipe.data['tags']:
    #         tag = Tag.objects.filter(id=tag_id).values()
    #         tag_list.append(tag[0])
    #     custom_data = serializer_recipe.data
    #     custom_data['tags'] = tag_list
    #     custom_data['author'] = User.objects.filter(id=request.user.id).values()[0]
    #     headers = self.get_success_headers(custom_data)
    #     return Response(custom_data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return Response(data={'OK':'OK'}, status=status.HTTP_200_OK)