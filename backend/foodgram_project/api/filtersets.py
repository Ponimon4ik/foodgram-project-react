from django.core.validators import MaxValueValidator
from django_filters import FilterSet, ModelMultipleChoiceFilter, NumberFilter

from recipes.models import Recipe, Tag


class FavoritedFilter(NumberFilter):

    def get_max_validator(self):
        return MaxValueValidator(1)


class RecipeFilter(FilterSet):

    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug'
    )

    is_favorited = FavoritedFilter(method='get_is_favorited')

    is_in_shopping_cart = FavoritedFilter(method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value == 1:
            return queryset.filter(favorite_recipe__user=user)
        return Recipe.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(shopping_cart__user=user)
        return Recipe.objects.all()
