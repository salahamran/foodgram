from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'username',
                    'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff',)
    search_fields = ('email', 'username')
    ordering = ('id',)
    fieldsets = BaseUserAdmin.fieldsets


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
