from rest_framework import status, viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from django.db.models import Sum

from recipes.models import (Recipe, Tag, Ingredient,
                            FavoriteRecipe, ShoppingCart)
from .serializers import (RecipeReadSerializer, RecipeWriteSerializer,
                          TagSerializer, IngredientSerializer,
                          FavoriteRecipeWriteSerializer,
                          ShoppingCartSerializer)
from .permissions import IsAuthorOrAdminOrReadOnly
from .pagination import CustomPagination
from .filtersets import RecipeFilter
from .utils import managing_subscriptions, create_pdf_shopping_cart


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, )
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrAdminOrReadOnly, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        methods=['post', 'delete'],
        detail=True
    )
    def favorite(self, request, pk=None):
        return managing_subscriptions(
            request, pk, FavoriteRecipe, FavoriteRecipeWriteSerializer
            )

    @action(
        methods=['post', 'delete'],
        detail=True,
    )
    def shopping_cart(self, request, pk=None):
        return managing_subscriptions(
            request, pk, ShoppingCart, ShoppingCartSerializer
            )

    @action(detail=False,)
    def download_shopping_cart(self, request):
        shopping_cart = request.user.shopping_cart.values(
            'recipe__ingredients_in_recipe__ingredient__name',
            'recipe__ingredients_in_recipe__ingredient__measurement_unit'
        ).annotate(quantity=Sum('recipe__ingredients_in_recipe__amount'))
        pdf_file = create_pdf_shopping_cart(shopping_cart)
        return FileResponse(
            pdf_file, as_attachment=True, filename='shopping_cart.pdf',
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name',)