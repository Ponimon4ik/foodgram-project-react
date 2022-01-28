from django.shortcuts import get_object_or_404
from django.db.models import Count
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag, TagRecipe)
from users.models import Follow, User
from users.serializers import CustomUserSerializer
from .utils import create_or_update_data

UNIQUE_FAVORITE_RECIPE = 'Рецепт уже находится в избранном'
SUBSCRIPTION_ERROR = 'Невозможно подписаться на себя'
DUPLICATE_SUBSCRIPTION = 'Вы уже подписаны на данного автора'
DUBLICATE_IN_SHOPPING_CART = 'Рецепт уже находится в списке покупок'
UNIQUE_INGREDIENT_IN_RECIPE = (
    'Удалите дубли ингредиентов {ingredient} из рецепта!'
)
UNIQUE_TAG_IN_RECIPE = (
    'Вы уже добавили тег {tag} в рецепт!'
)


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

    class Meta:

        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):

    tags = TagRecipeSerializer(many=True, source='tags_in_recipe')
    author = CustomUserSerializer()
    ingredients = IngredientRecipeSerializer(
        many=True, source='ingredients_in_recipe'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:

        model = Recipe
        read_only_fields = ('__all__',)
        exclude = ['pub_date']

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorite_recipe.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):

    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
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

    class Meta:
        model = Recipe
        exclude = ['pub_date']

    def validate_tags(self, value):
        tags = value
        verified = []
        for tag in tags:
            if tag not in verified:
                verified.append(tag)
            else:
                raise serializers.ValidationError(
                    UNIQUE_TAG_IN_RECIPE.format(tag=tag.name))
        return value

    def validate_ingredients(self, value):
        ingredients = value
        verified_id = []
        for ingredient in ingredients:
            if ingredient['ingredient'] not in verified_id:
                verified_id.append(ingredient['ingredient'])
            else:
                raise serializers.ValidationError(
                    [
                        {
                            'id': [
                                UNIQUE_INGREDIENT_IN_RECIPE.format(
                                    ingredient=ingredient['ingredient'].name
                                )
                            ]
                        }
                    ]
                )
        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients_in_recipe')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        return create_or_update_data(ingredients_data, tags_data, recipe)

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients_in_recipe', None)
        tags_data = validated_data.pop('tags', None)
        super().update(instance, validated_data)
        return create_or_update_data(
            ingredients_data, tags_data, instance, action='update')

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


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


class RecipeWithoutIngredients(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe
        read_only_fields = ('__all__', )


class FavoriteRecipeWriteSerializer(serializers.ModelSerializer):

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
        read_only_fields = ('__all__', )

    def to_representation(self, instance):
        return RecipeWithoutIngredients(instance.recipe).data


class FollowReadSerializer(serializers.ModelSerializer):

    recipes = RecipeWithoutIngredients(
        many=True
    )
    recipes_count = serializers.IntegerField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'recipes', 'recipes_count', 'is_subscribed'
        )
        read_only_fields = ('__all__', )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return user.follower.filter(following=obj).exists()


class FollowSerializer(serializers.ModelSerializer):

    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ('user', 'following')
        model = Follow
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'following'],
                message=DUPLICATE_SUBSCRIPTION
            )
        ]

    def validate_following(self, value):
        if value == self.context['request'].user:
            raise serializers.ValidationError(detail=SUBSCRIPTION_ERROR)
        return value

    def to_representation(self, instance):
        queryset = User.objects.filter(
            id=instance.following.id).annotate(
            recipes_count=Count('recipes')
        ).order_by('id')
        obj = get_object_or_404(queryset, id=instance.following.id)
        return FollowReadSerializer(
            obj,
            context={'request': self.context['request']}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):

    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ('user', 'recipe')
        model = ShoppingCart
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
                message=DUBLICATE_IN_SHOPPING_CART
            )
        ]

    def to_representation(self, instance):
        return RecipeWithoutIngredients(
            instance.recipe, context=self.context
        ).data
