from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CreateRoomForm, EditRoomForm
from .models import Membership, Room
from .services import (
    create_room,
    get_public_rooms,
    get_user_rooms,
    is_member,
    is_owner_or_admin,
    join_room,
    leave_room,
)


@login_required
def lobby_view(request):
    """Main landing page — lists rooms the user belongs to + discoverable rooms."""
    my_rooms = get_user_rooms(request.user)
    public_rooms = get_public_rooms().exclude(memberships__user=request.user)

    return render(request, "rooms/lobby.html", {
        "my_rooms": my_rooms,
        "public_rooms": public_rooms,
    })


@login_required
def create_room_view(request):
    form = CreateRoomForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        room = create_room(
            user=request.user,
            name=form.cleaned_data["name"],
            description=form.cleaned_data["description"],
            room_type=form.cleaned_data["room_type"],
            is_private=form.cleaned_data["is_private"],
        )
        messages.success(request, f'Room "{room.name}" created.')
        return redirect("rooms:detail", slug=room.slug)

    return render(request, "rooms/create_room.html", {"form": form})


@login_required
def room_detail_view(request, slug):
    """
    Entry point for a chat room. The actual messaging happens over WebSocket;
    this view just checks membership and renders the shell template.
    """
    room = get_object_or_404(Room, slug=slug)

    if room.is_private and not is_member(request.user, room):
        messages.error(request, "This room is private.")
        return redirect("rooms:lobby")

    membership = Membership.objects.filter(user=request.user, room=room).first()

    return render(request, "rooms/room.html", {
        "room": room,
        "membership": membership,
        "is_member": membership is not None,
    })


@login_required
def join_room_view(request, slug):
    room = get_object_or_404(Room, slug=slug)

    if room.is_private:
        messages.error(request, "You need an invitation to join this room.")
        return redirect("rooms:lobby")

    _, created = join_room(request.user, room)
    if created:
        messages.success(request, f'You joined "{room.name}".')

    return redirect("rooms:detail", slug=room.slug)


@login_required
def leave_room_view(request, slug):
    room = get_object_or_404(Room, slug=slug)

    if request.method == "POST":
        try:
            left = leave_room(request.user, room)
            if left:
                messages.success(request, f'You left "{room.name}".')
            return redirect("rooms:lobby")
        except ValueError as e:
            messages.error(request, str(e))
            return redirect("rooms:detail", slug=room.slug)

    return render(request, "rooms/leave_room.html", {"room": room})


@login_required
def edit_room_view(request, slug):
    room = get_object_or_404(Room, slug=slug)

    if not is_owner_or_admin(request.user, room):
        messages.error(request, "You don't have permission to edit this room.")
        return redirect("rooms:detail", slug=room.slug)

    form = EditRoomForm(request.POST or None, instance=room)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Room updated.")
        return redirect("rooms:detail", slug=room.slug)

    return render(request, "rooms/edit_room.html", {"form": form, "room": room})


@login_required
def delete_room_view(request, slug):
    room = get_object_or_404(Room, slug=slug)

    if not is_owner_or_admin(request.user, room):
        messages.error(request, "Only the room owner can delete this room.")
        return redirect("rooms:detail", slug=room.slug)

    if request.method == "POST":
        room.delete()
        messages.success(request, f'Room "{room.name}" deleted.')
        return redirect("rooms:lobby")

    return render(request, "rooms/delete_room.html", {"room": room})


@login_required
def members_view(request, slug):
    room = get_object_or_404(Room, slug=slug)

    if not is_member(request.user, room):
        return redirect("rooms:lobby")

    memberships = (
        Membership.objects
        .filter(room=room)
        .select_related("user", "user__profile")
        .order_by("role", "created_at")
    )
    user_membership = memberships.filter(user=request.user).first()

    return render(request, "rooms/members.html", {
        "room": room,
        "memberships": memberships,
        "user_membership": user_membership,
        "can_manage": is_owner_or_admin(request.user, room),
    })