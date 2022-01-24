from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from recipes.models import (Recipe, Tag, Ingredient,
                            FavoriteRecipe, ShoppingCart)
from user.models import (Follow, User)
from .serializers import (RecipeReadSerializer, RecipeWriteSerializer,
                          TagSerializer, IngredientSerializer,
                          FavoriteRecipeWriteSerializer,
                          ShoppingCartSerializer)

def managing_subscriptions(request, pk, model, model_serializer):
    
    NO_IN_SHOPPING_CART = 'Рецепт не был в списке покупок'
    NO_IN_FAVORITE = 'Рецепт не был в избранном'
    NO_SUBSCRIPTION_ON_AUTHOR = 'Вы не были подписаны на данного автора'

    if model in [ShoppingCart, FavoriteRecipe]:
        key_data = 'recipe'
        model_for_check = Recipe
    else:
        key_data = 'following'
        model_for_check = User
    data = {
        'user': request.user.id,
        key_data: pk
    }
    get_object_or_404(model_for_check, pk=pk)
    if request.method != 'DELETE':
        serializer = model_serializer(
            data=data, context={'request': request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    try:
        obj = model.objects.get(**data)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ObjectDoesNotExist:
        error_msg = {
            ShoppingCart: NO_IN_SHOPPING_CART,
            FavoriteRecipe: NO_IN_FAVORITE,
            Follow: NO_SUBSCRIPTION_ON_AUTHOR
            }
        return Response(
            {'errors': error_msg[model]},
            status=status.HTTP_400_BAD_REQUEST
            )


def shopping_cart(self, request, pk=None):
    get_object_or_404(Recipe, pk=pk)
    data = {
        'user': request.user.id,
        'recipe': pk
    }
    if request.method != 'DELETE':
        serializer = ShoppingCartSerializer(
            data=data, context={'request': request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    try:
        shoping_list_recipe = ShoppingCart.objects.get(**data)
        self.perform_destroy(shoping_list_recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ObjectDoesNotExist:
        return Response(
            {'errors': 'Рецепт не был в списке покупок'},
            status=status.HTTP_400_BAD_REQUEST
            )



def favorite(self, request, pk=None):
    get_object_or_404(Recipe, pk=pk)
    data = {
        'user': request.user.id,
        'recipe': pk
    }
    if request.method != 'DELETE':
        serializer = FavoriteRecipeWriteSerializer(
            data=data, context={'request': request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    try:
        favorite_recipe = FavoriteRecipe.objects.get(**data)
        self.perform_destroy(favorite_recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ObjectDoesNotExist:
        return Response(
                {'errors': 'Рецепт не был в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )


def create_or_delete_subscription(self, request, pk=None):
    get_object_or_404(User, pk=pk)
    data = {
        'user': request.user,
        'following': pk
        }
    if request.method != 'DELETE':
        serializer = FollowSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED) 
    try:
        subscription = Follow.objects.get(**data)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ObjectDoesNotExist:
        return Response(
            {'errors': 'Вы не были подписаны на данного автора'},
            status=status.HTTP_400_BAD_REQUEST
            )
         