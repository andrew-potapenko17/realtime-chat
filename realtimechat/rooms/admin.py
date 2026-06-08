from django.contrib import admin

from .models import Membership, Room


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    readonly_fields = ("created_at",)
    fields = ("user", "role", "last_read_at", "created_at")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "room_type", "is_private", "created_by", "created_at")
    list_filter = ("room_type", "is_private")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    inlines = [MembershipInline]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "room", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("user__email", "room__name")
    readonly_fields = ("created_at",)