from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import TimestampedModel


def avatar_upload_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    return f"avatars/user_{instance.user_id}/{filename}"


class UserProfile(TimestampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        null=True,
        blank=True,
    )
    bio = models.CharField(max_length=160, blank=True, default="")

    # Presence — updated by WebSocket consumer on connect/disconnect
    is_online = models.BooleanField(default=False, db_index=True)
    last_seen = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "user profile"
        verbose_name_plural = "user profiles"

    def __str__(self):
        return f"Profile({self.user})"

    def mark_online(self):
        self.is_online = True
        self.save(update_fields=["is_online", "last_seen"])

    def mark_offline(self):
        self.is_online = False
        self.last_seen = timezone.now()
        self.save(update_fields=["is_online", "last_seen"])