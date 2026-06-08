from django.conf import settings
from django.db import models
from django.utils.text import slugify

from core.models import TimestampedModel


class Room(TimestampedModel):
    class RoomType(models.TextChoices):
        GROUP = "group", "Group"
        DIRECT = "direct", "Direct message"
        CHANNEL = "channel", "Channel"

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110, unique=True, db_index=True)
    description = models.CharField(max_length=300, blank=True, default="")
    room_type = models.CharField(
        max_length=10,
        choices=RoomType.choices,
        default=RoomType.GROUP,
        db_index=True,
    )
    is_private = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_rooms",
    )

    class Meta:
        verbose_name = "room"
        verbose_name_plural = "rooms"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.room_type})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Membership(TimestampedModel):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    # Tracks the last message the user has seen — used to compute unread count
    last_read_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = "membership"
        verbose_name_plural = "memberships"
        unique_together = [("user", "room")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} in {self.room} as {self.role}"