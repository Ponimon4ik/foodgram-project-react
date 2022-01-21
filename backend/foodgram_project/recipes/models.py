from django.db import models

from users.models import User


class Tag(models.Model):

    name = models.TextField(
        verbose_name='Название',
        max_length=50
    )
    color = models.CharField(
        verbose_name='Цвет',
        unique=True, max_length=50
    )
    slug = models.SlugField(
        verbose_name='Ключ',
        unique=True, max_length=50
    )


class Ingredient(models.Model):

    name = models.TextField(
        verbose_name='Название',
        max_length=50,
    )
    measurement_unit = models.CharField(
        verbose_name='единица измерения', max_length=50
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_ingredient')
        ]


class Recipe(models.Model):

    author = models.ForeignKey(
        User, verbose_name='Автор', on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Ингредиенты', through='IngredientRecipe',
        related_name='recipe'
    )
    tags = models.ManyToManyField(
        Tag, verbose_name='Теги', through='TagRecipe',
        related_name='recipe'
    )
    image = models.ImageField(
        verbose_name='Картинка', upload_to='recipes/'
    )
    name = models.TextField(
        verbose_name='Название', max_length=200
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления', help_text='минут'
    )


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT,
        related_name='ingredients_in_recipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe')
    amount = models.PositiveIntegerField(verbose_name='Количество')


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tags_in_recipe'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='tags_in_recipe'
    )


class FavoriteRecipe(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'

            )
        ]

class ShoppingCart(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )