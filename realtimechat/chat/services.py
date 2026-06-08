from django.utils import timezone

from rooms.models import Membership

from .models import Message, MessageReadReceipt

HISTORY_PAGE_SIZE = 50


def get_room_history(room, before=None, limit=HISTORY_PAGE_SIZE):
    qs = (
        Message.objects
        .filter(room=room, is_deleted=False)
        .select_related("sender", "reply_to__sender")
        .order_by("-created_at")
    )
    if before:
        qs = qs.filter(id__lt=before)
    return list(reversed(qs[:limit]))


def save_message(room, sender, content, reply_to_id=None, msg_type=Message.MessageType.TEXT):
    return Message.objects.create(
        room=room,
        sender=sender,
        content=content,
        msg_type=msg_type,
        reply_to_id=reply_to_id,
    )


def delete_message(message, user):
    is_sender = message.sender_id == user.id
    is_admin = Membership.objects.filter(
        user=user,
        room=message.room,
        role__in=[Membership.Role.OWNER, Membership.Role.ADMIN],
    ).exists()

    if not (is_sender or is_admin):
        raise PermissionError("You cannot delete this message.")

    message.soft_delete()
    return True


def mark_room_read(user, room):
    Membership.objects.filter(user=user, room=room).update(last_read_at=timezone.now())


def get_unread_count(user, room):
    membership = Membership.objects.filter(user=user, room=room).first()
    if not membership or not membership.last_read_at:
        return 0
    return Message.objects.filter(
        room=room,
        is_deleted=False,
        created_at__gt=membership.last_read_at,
    ).count()


def serialize_message(message):
    reply = None
    if message.reply_to and not message.reply_to.is_deleted:
        reply = {
            "id": message.reply_to.id,
            "sender": message.reply_to.sender.username if message.reply_to.sender else "deleted",
            "content": message.reply_to.content[:80],
        }

    return {
        "id": message.id,
        "room": message.room_id,
        "sender": message.sender.username if message.sender else "deleted",
        "sender_id": message.sender_id,
        "content": message.content if not message.is_deleted else "",
        "msg_type": message.msg_type,
        "is_deleted": message.is_deleted,
        "reply_to": reply,
        "timestamp": message.created_at.isoformat(),
    }