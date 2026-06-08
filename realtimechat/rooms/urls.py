from django.urls import path

from . import views

app_name = "rooms"

urlpatterns = [
    path("", views.lobby_view, name="lobby"),
    path("create/", views.create_room_view, name="create"),
    path("<slug:slug>/", views.room_detail_view, name="detail"),
    path("<slug:slug>/join/", views.join_room_view, name="join"),
    path("<slug:slug>/leave/", views.leave_room_view, name="leave"),
    path("<slug:slug>/edit/", views.edit_room_view, name="edit"),
    path("<slug:slug>/delete/", views.delete_room_view, name="delete"),
    path("<slug:slug>/members/", views.members_view, name="members"),
]