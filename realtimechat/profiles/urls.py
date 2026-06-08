from django.urls import path

from . import views

app_name = "profiles"

urlpatterns = [
    path("edit/", views.edit_profile_view, name="edit"),
    path("avatar/remove/", views.remove_avatar_view, name="remove-avatar"),
    path("<str:username>/", views.profile_view, name="profile"),
]