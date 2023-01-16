from django.contrib import admin

from .models import Follow, User


class UserAdmin(admin.ModelAdmin):
    """
    Параметры админ зоны пользователя.
    """
    list_display = (
        'id',
        'username',
        'email',
        'role',
        'first_name',
        'last_name'
    )
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'
    list_display_links = ('id', 'username')


class FollowAdmin(admin.ModelAdmin):
    """
    Параметры админ зоны подписков.
    """
    list_display = (
        'id',
        'user',
        'author'
    )
    list_display_links = ('id', 'user')
    search_fields = ('user',)


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
