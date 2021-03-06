import io

from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.response import Response

from recipes.models import (FavoriteRecipe, Recipe,
                            ShoppingCart, IngredientRecipe,
                            TagRecipe)

from users.models import Follow, User

NO_IN_SHOPPING_CART = 'Рецепт не был в списке покупок'
NO_IN_FAVORITE = 'Рецепт не был в избранном'
NO_SUBSCRIPTION_ON_AUTHOR = 'Вы не были подписаны на данного автора'
HEADING_PDF_SHOPPING_CART = 'Список покупок'


def managing_subscriptions(request, pk, model, model_serializer):

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
    except model.DoesNotExist:
        error_msg = {
            ShoppingCart: NO_IN_SHOPPING_CART,
            FavoriteRecipe: NO_IN_FAVORITE,
            Follow: NO_SUBSCRIPTION_ON_AUTHOR
        }
        return Response(
            {'errors': error_msg[model]},
            status=status.HTTP_400_BAD_REQUEST
        )


def create_or_update_data(
        ingredients_data, tags_data, obj, action=None
):
    if ingredients_data is not None:
        if action == 'update':
            obj.ingredients.clear()
        for ingredient in ingredients_data:
            IngredientRecipe.objects.create(
                recipe=obj,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
    if tags_data is not None:
        if action == 'update':
            obj.tags.clear()
        for tag in tags_data:
            TagRecipe.objects.create(
                recipe=obj, tag=tag
            )
    return obj


def create_pdf_shopping_cart(shopping_cart):
    buffer = io.BytesIO()
    pdfmetrics.registerFont(TTFont('FreeSans', 'backend_static/FreeSans.ttf'))
    p = canvas.Canvas(buffer)
    p.setFont('FreeSans', 20)
    axis_y = 780
    p.drawString(250, 800, HEADING_PDF_SHOPPING_CART)
    p.setFont('FreeSans', 8)
    for ingredient in shopping_cart:
        (
            name,
            measurement_unit,
            amount
        ) = ingredient.values()
        p.drawString(
            100,
            axis_y,
            f'{name} {amount} {measurement_unit}'
        )
        axis_y -= 15
        if axis_y <= 0:
            axis_y = 800
            p.showPage()
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
