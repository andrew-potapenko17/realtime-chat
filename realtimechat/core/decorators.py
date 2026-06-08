from functools import wraps
 
from django.http import JsonResponse
from django.shortcuts import redirect
 
 
def ajax_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required."}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper
 
 
def require_membership(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from rooms.models import Membership, Room
        slug = kwargs.get("slug")
        try:
            room = Room.objects.get(slug=slug)
        except Room.DoesNotExist:
            return redirect("rooms:lobby")
 
        if not Membership.objects.filter(user=request.user, room=room).exists():
            return redirect("rooms:lobby")
 
        return view_func(request, *args, **kwargs)
    return wrapper
 