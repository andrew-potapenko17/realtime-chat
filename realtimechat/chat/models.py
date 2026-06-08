from django.conf import settings
from django.db import models

from core.models import TimestampedModel
from rooms.models import Room


def message_file_upload_path(instance, filename):
    return f"chat/room_{instance.room_id}/{filename}"


class Message(TimestampedModel):
    class MessageType(models.TextChoices):
        TEXT = "text", "Text"
        IMAGE = "image", "Image"
        FILE = "file", "File"
        SYSTEM = "system", "System"  # e.g. "Alice joined the room"

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="messages",
        db_index=True,
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="messages",
    )
    # Threading — nullable self-FK for reply chains
    reply_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
    )

    content = models.TextField(blank=True, default="")
    msg_type = models.CharField(
        max_length=10,
        choices=MessageType.choices,
        default=MessageType.TEXT,
        db_index=True,
    )
    file = models.FileField(
        upload_to=message_file_upload_path,
        null=True,
        blank=True,
    )

    # Soft-delete: keeps read receipts and reply references intact
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "message"
        verbose_name_plural = "messages"
        ordering = ["created_at"]
        indexes = [
            # Fast latest-N-messages-per-room query
            models.Index(fields=["room", "created_at"]),
            # Fast unread count query (room + created_at > last_read_at)
            models.Index(fields=["room", "is_deleted", "created_at"]),
        ]

    def __str__(self):
        preview = self.content[:40] if self.content else f"[{self.msg_type}]"
        return f"Message({self.room_id}) by {self.sender_id}: {preview}"

    def soft_delete(self):
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.content = ""
        self.save(update_fields=["is_deleted", "deleted_at", "content"])


class MessageReadReceipt(models.Model):
    """Tracks which users have read which messages."""

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="read_receipts",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="read_receipts",
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "read receipt"
        verbose_name_plural = "read receipts"
        unique_together = [("message", "user")]
        indexes = [
            models.Index(fields=["user", "message"]),
        ]

    def __str__(self):
        return f"{self.user} read message {self.message_id} at {self.read_at}"