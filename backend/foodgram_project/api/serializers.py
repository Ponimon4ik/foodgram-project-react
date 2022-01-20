from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Recipe, TagRecipe, Tag, Ingredient,
                            IngredientRecipe, FavoriteRecipe)
from users.models import User
from users.serializers import CustomUserSerializer

UNIQUE_FAVORITE_RECIPE = 'Рецепт уже находится в избранном'


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
    amount = serializers.IntegerField() # поробовать убрать

    class Meta:

        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):

    author = CustomUserSerializer()
    ingredients = IngredientRecipeSerializer(
        many=True, source='ingredients_in_recipe'
    )
    tags = TagRecipeSerializer(many=True, source='tags_in_recipe')
    is_favorited = serializers.SerializerMethodField()

    class Meta:

        model = Recipe
        fields = '__all__'
        read_only_fields = ('__all__',)

    # def is_favorited(self, obj):
    #     user = self.request.user
    #     recipe = user.favorite_recipe.recipe
    #     if recipe == obj:
    #         return True
    #     return False



class RecipeWriteSerializer(serializers.ModelSerializer):
    # HiddenField + убрать из метода save() во вьюсете
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
    name = serializers.CharField() # попробовать убрать
    text = serializers.CharField() # попробовать убрать 
    cooking_time = serializers.IntegerField() # попробовать убрать

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


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__', )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__', )


class FavoriteRecipeReadSerializer(serializers.ModelSerializer):
    # Попробовать нереляционные поля оставить source = recipe.id.
    id = serializers.SlugRelatedField(
        source='recipe', slug_field='id',
        queryset=Recipe.objects.all()
    )
    name = serializers.SlugRelatedField(
        source='recipe', slug_field='name',
        queryset=Recipe.objects.all()
    )
    image = Base64ImageField(
        source='recipe.image',
    )
    cooking_time = serializers.SlugRelatedField(
        source='recipe', slug_field='cooking_time',
        queryset=Recipe.objects.all()
    )

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = FavoriteRecipe
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteRecipeWriteSerializer(serializers.ModelSerializer):
    # HiddenField + убрать из метода save() во вьюсете default=serializers.CurrentUserDefault()
    # Попробовать убрать вообще
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )# убрать queryset + read_only == true или попробовать вообще убрать
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all(),

                                                )

    class Meta:
        fields = ('user', 'recipe')
        model = FavoriteRecipe
        validators = [
            UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=('user', 'recipe'),
                message=UNIQUE_FAVORITE_RECIPE,
            )
        ]
        #read_only = all
    def to_representation(self, instance):
        return FavoriteRecipeReadSerializer(instance).data
