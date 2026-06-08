from django.urls import path
 
from . import views
 
app_name = "chat"
 
urlpatterns = [
    path("<slug:slug>/history/", views.message_history_view, name="history"),
    path("unread/", views.unread_counts_view, name="unread"),
]
 