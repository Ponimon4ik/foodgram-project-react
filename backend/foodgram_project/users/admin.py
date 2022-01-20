from django.contrib import admin

from .models import User, Follow


class UserAdmin(admin.ModelAdmin):

    list_display = ('pk', 'username', 'email', 'first_name', 'last_name')
    search_fields = ('username',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Follow)
