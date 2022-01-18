from rest_framework import status, permissions, mixins, viewsets, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core import serializers

from recipes.models import Recipe
from .serializers import RecipeReadSerializer, RecipeWriteSerializer
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
