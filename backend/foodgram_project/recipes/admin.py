from django.contrib import admin
from django.db.models import fields, Count

from .models import (Recipe, Tag, TagRecipe,
                     Ingredient, IngredientRecipe,
                     FavoriteRecipe, ShoppingCart)

class RecipeAdmin(admin.ModelAdmin):
    fields = ('pk', 'name', 'author', 'follow_count')
    readonly_fields = ('order_number',)
    list_display = ('pk', 'name', 'author')
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
