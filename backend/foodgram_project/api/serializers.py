from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Recipe, TagRecipe, Tag, Ingredient, IngredientRecipe


class IngredientRecipeSerializer(serializers.ModelSerializer):

    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:

        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):

    ingredients = IngredientRecipeSerializer(
        many=True, source='recipes_ingredients_list'
    )

    class Meta:

        model = Recipe
        fields = '__all__'
