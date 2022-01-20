from django.contrib import admin

from .models import (Recipe, Tag, TagRecipe,
                     Ingredient, IngredientRecipe, FavoriteRecipe)

admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(TagRecipe)
admin.site.register(Ingredient)
admin.site.register(IngredientRecipe)
admin.site.register(FavoriteRecipe)
