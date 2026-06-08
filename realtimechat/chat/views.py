import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from rooms.models import Room
from rooms.services import is_member

from .services import get_room_history, get_unread_count, serialize_message


@login_required
@require_GET
def message_history_view(request, slug):
    """
    GET /chat/<slug>/history/?before=<message_id>
    Returns paginated message history as JSON.
    Used by the frontend to load older messages on scroll.
    """
    room = get_object_or_404(Room, slug=slug)

    if not is_member(request.user, room):
        return JsonResponse({"error": "Not a member of this room."}, status=403)

    before = request.GET.get("before")
    messages = get_room_history(room, before=before)

    return JsonResponse({
        "messages": [serialize_message(m) for m in messages],
        "has_more": len(messages) == 50,
    })


@login_required
@require_GET
def unread_counts_view(request):
    """
    GET /chat/unread/
    Returns unread message counts for all rooms the user belongs to.
    Used by the sidebar to show unread badges.
    """
    from rooms.models import Room
    rooms = Room.objects.filter(memberships__user=request.user)
    counts = {
        room.slug: get_unread_count(request.user, room)
        for room in rooms
    }
    return JsonResponse({"unread": counts})