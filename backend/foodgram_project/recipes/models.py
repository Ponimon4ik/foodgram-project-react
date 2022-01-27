from django.db import models

from users.models import User


class Tag(models.Model):

    name = models.TextField(
        verbose_name='Название',
        max_length=50, unique=True
    )
    color = models.CharField(
        verbose_name='Цвет',
        unique=True, max_length=50,
    )
    slug = models.SlugField(
        verbose_name='Ключ',
        unique=True, max_length=50
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = [
            models.UniqueConstraint(fields=['name', 'color', 'slug'],
                                    name='unique_tag')
        ]

    def __str__(self):
        return (
            f'{self.name}, '
            f'{self.color}, '
            f'{self.slug}'
        )


class Ingredient(models.Model):

    name = models.TextField(
        verbose_name='Название',
        max_length=50,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения', max_length=50
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_ingredient')
        ]

    def __str__(self):
        return (
            f'{self.name}, '
            f'{self.measurement_unit}'
        )


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
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return(
            f'{self.author.username}, '
            f'{self.name}, '
            f'{self.text[:10]}, '
            f'{self.cooking_time}, '
            f'{self.pub_date}'
        )


class IngredientRecipe(models.Model):

    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT,
        related_name='ingredients_in_recipe'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='ingredients_in_recipe'
    )
    amount = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        return(
            f'{self.ingredient.name}, '
            f'{self.recipe.name}, '
            f'{self.amount}'
        )


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

    class Meta:
        verbose_name = 'Тег в рецепте'
        verbose_name_plural = 'Теги в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['tag', 'recipe'],
                name='unique_tag_in_recipe'
            )
        ]

    def __str__(self):
        return(
            f'{self.tag.name}, '
            f'{self.recipe.name}, '
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
        verbose_name = 'Тег в рецепте'
        verbose_name_plural = 'Теги в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            )
        ]

    def __str__(self):
        return(
            f'{self.user.username}, '
            f'{self.recipe.name},'
        )


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

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списках покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_shopping_list'
            )
        ]

    def __str__(self):
        return(
            f'{self.user.username}, '
            f'{self.recipe.name}'
        )
