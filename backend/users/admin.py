from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Subscription, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'id', 'username',
                    'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_display_links = ('email', 'id', 'username')
    ordering = ('id',)
    fieldsets = BaseUserAdmin.fieldsets


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'author')
