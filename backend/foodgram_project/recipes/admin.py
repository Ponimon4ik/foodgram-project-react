from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag, TagRecipe)


class RecipeAdmin(admin.ModelAdmin):

    list_display = ('pk', 'name', 'author', 'follow_count')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'

    def follow_count(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj).count()


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(TagRecipe)
admin.site.register(Ingredient)
admin.site.register(IngredientRecipe)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingCart)
