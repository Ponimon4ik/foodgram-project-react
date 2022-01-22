from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from drf_extra_fields.fields import Base64ImageField
from django.db.models import Count

from recipes.models import (Recipe, TagRecipe, Tag, Ingredient,
                            IngredientRecipe, FavoriteRecipe, ShoppingCart)
from users.models import User, Follow
from users.serializers import CustomUserSerializer

UNIQUE_FAVORITE_RECIPE = 'Рецепт уже находится в избранном'
SUBSCRIPTION_ERROR = 'Невозможно подписаться на себя'
DUPLICATE_SUBSCRIPTION = 'Вы уже подписаны на данного автора'
DUBLICATE_IN_SHOPPING_CART = 'Рецепт уже находится в списке покупок'


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

    author = CustomUserSerializer()
    ingredients = IngredientRecipeSerializer(
        many=True, source='ingredients_in_recipe'
    )
    tags = TagRecipeSerializer(many=True, source='tags_in_recipe')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:

        model = Recipe
        fields = '__all__'
        read_only_fields = ('__all__',)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user.favorite_recipe.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
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


class AuthorsOrFavoriteRecipeSerializer(serializers.ModelSerializer):

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
        return AuthorsOrFavoriteRecipeSerializer(instance.recipe).data


class FollowReadSerializer(serializers.ModelSerializer):

    recipes = AuthorsOrFavoriteRecipeSerializer(
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
        obj = queryset.get(id=instance.following.id)
        return FollowReadSerializer(obj).data


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
        return AuthorsOrFavoriteRecipeSerializer(
            instance.recipe, context=self.context
        ).data
