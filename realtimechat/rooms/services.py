from django.db import transaction

from .models import Membership, Room


def create_room(user, name, description="", room_type=Room.RoomType.GROUP, is_private=False):
    """Create a room and make the creator its owner in one transaction."""
    with transaction.atomic():
        room = Room.objects.create(
            name=name,
            description=description,
            room_type=room_type,
            is_private=is_private,
            created_by=user,
        )
        Membership.objects.create(
            user=user,
            room=room,
            role=Membership.Role.OWNER,
        )
    return room


def join_room(user, room):
    """Add a user to a room as a member. Returns (membership, created)."""
    return Membership.objects.get_or_create(
        user=user,
        room=room,
        defaults={"role": Membership.Role.MEMBER},
    )


def leave_room(user, room):
    """Remove a user from a room. Owners cannot leave without transferring ownership."""
    membership = Membership.objects.filter(user=user, room=room).first()
    if not membership:
        return False
    if membership.role == Membership.Role.OWNER:
        raise ValueError("Owner must transfer ownership before leaving.")
    membership.delete()
    return True


def get_user_rooms(user):
    """Return all rooms the user is a member of, with unread counts."""
    return (
        Room.objects
        .filter(memberships__user=user)
        .select_related("created_by")
        .prefetch_related("memberships")
        .order_by("name")
    )


def get_public_rooms():
    """Return all non-private, non-direct rooms."""
    return Room.objects.filter(
        is_private=False,
    ).exclude(
        room_type=Room.RoomType.DIRECT,
    ).order_by("name")


def is_member(user, room):
    return Membership.objects.filter(user=user, room=room).exists()


def is_owner_or_admin(user, room):
    return Membership.objects.filter(
        user=user,
        room=room,
        role__in=[Membership.Role.OWNER, Membership.Role.ADMIN],
    ).exists()