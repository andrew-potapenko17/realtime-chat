from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_online", "last_seen", "created_at")
    list_filter = ("is_online",)
    search_fields = ("user__email", "user__username")
    readonly_fields = ("is_online", "last_seen", "created_at", "updated_at")
    fields = ("user", "avatar", "bio", "is_online", "last_seen", "created_at", "updated_at")