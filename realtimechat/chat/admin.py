from django.contrib import admin
 
from .models import Message, MessageReadReceipt
 
 
class MessageReadReceiptInline(admin.TabularInline):
    model = MessageReadReceipt
    extra = 0
    readonly_fields = ("user", "read_at")
 
 
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "sender", "msg_type", "is_deleted", "created_at")
    list_filter = ("msg_type", "is_deleted", "room")
    search_fields = ("content", "sender__email", "room__name")
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    raw_id_fields = ("sender", "room", "reply_to")
    inlines = [MessageReadReceiptInline]
 
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("sender", "room")
 
 
@admin.register(MessageReadReceipt)
class MessageReadReceiptAdmin(admin.ModelAdmin):
    list_display = ("message", "user", "read_at")
    search_fields = ("user__email",)
    readonly_fields = ("read_at",)
 