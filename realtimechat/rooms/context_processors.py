from .models import Room
 
 
def sidebar_rooms(request):
    """Makes the user's room list available in every template for the sidebar."""
    if not request.user.is_authenticated:
        return {"sidebar_rooms": []}
 
    rooms = (
        Room.objects
        .filter(memberships__user=request.user)
        .only("name", "slug")
        .order_by("name")
    )
    return {"sidebar_rooms": rooms}
 