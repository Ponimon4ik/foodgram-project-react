from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Recipe, TagRecipe, Tag, Ingredient, IngredientRecipe
from users.serializers import CustomUserSerializer


class TagRecipeSerializer(serializers.ModelSerializer):

    id = serializers.SlugRelatedField(
        source='tag', slug_field='id', queryset=Tag.objects.all()
    )
    name = serializers.ReadOnlyField(source='tag.name')
    color = serializers.ReadOnlyField(source='tag.color')
    slug = serializers.ReadOnlyField(source='tag.slug')

    class Meta:

        model = TagRecipe
        fields = ('id', 'name', 'color', 'slug')


class IngredientRecipeSerializer(serializers.ModelSerializer):

    id = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='id', queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:

        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):

    author = CustomUserSerializer()
    ingredients = IngredientRecipeSerializer(
        many=True, source='ingredients_in_recipe'
    )
    tags = TagRecipeSerializer(many=True, source='tags_in_recipe')

    class Meta:

        model = Recipe
        fields = '__all__'


class RecipeWriteSerializer(serializers.ModelSerializer):

    author = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    ingredients = IngredientRecipeSerializer(
        many=True, source='ingredients_in_recipe'
    )
    tags = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    name = serializers.CharField()
    text = serializers.CharField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients_in_recipe')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
        for tag in tags:
            TagRecipe.objects.create(
                recipe=recipe, tag=tag
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients_in_recipe', None)
        tags_data = validated_data.pop('tags', None)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        if ingredients_data:
            instance.ingredients.clear()
            for ingredient in ingredients_data:
                IngredientRecipe.objects.create(
                    recipe=instance,
                    ingredient=ingredient['ingredient'],
                    amount=ingredient['amount']
                )
        if tags_data:
            instance.tags.clear()
            for tag in tags_data:
                TagRecipe.objects.create(
                    recipe=instance, tag=tag
                )
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance).data
