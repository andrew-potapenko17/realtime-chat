import json
 
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.shortcuts import get_object_or_404
 
from rooms.models import Membership, Room
 
from .services import (
    delete_message,
    get_room_history,
    mark_room_read,
    save_message,
    serialize_message,
)
from .models import Message
 
 
class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    Handles one WebSocket connection for one user in one room.
 
    Supported incoming message types:
      chat_message  — send a text message
      delete_message — soft-delete a message (sender or admin only)
      typing        — broadcast typing indicator
      read          — mark the room as read for this user
 
    Outgoing message types:
      history       — initial message history on connect
      chat_message  — a new message broadcast to the group
      message_deleted — notifies group a message was soft-deleted
      typing        — typing indicator forwarded to group
      presence      — online/offline status of a user
      error         — something went wrong
    """
 
    # ── Connection lifecycle ───────────────────────────────────────────────────
 
    async def connect(self):
        self.user = self.scope["user"]
        self.slug = self.scope["url_route"]["kwargs"]["slug"]
        self.group_name = f"chat_{self.slug}"
 
        # Reject unauthenticated connections immediately
        if not self.user.is_authenticated:
            await self.close(code=4001)
            return
 
        # Reject if the user is not a member of this room
        self.room = await self.get_room()
        if not self.room:
            await self.close(code=4004)
            return
 
        is_member = await self.check_membership()
        if not is_member:
            await self.close(code=4003)
            return
 
        # Join the channel group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
 
        # Send message history to this connection only
        history = await self.load_history()
        await self.send_json({
            "type": "history",
            "messages": history,
        })
 
        # Mark the room as read and broadcast presence
        await self.set_online(True)
        await self.channel_layer.group_send(self.group_name, {
            "type": "presence",
            "username": self.user.username,
            "is_online": True,
        })
 
    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.set_online(False)
            await self.channel_layer.group_send(self.group_name, {
                "type": "presence",
                "username": self.user.username,
                "is_online": False,
            })
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
 
    # ── Incoming messages ──────────────────────────────────────────────────────
 
    async def receive_json(self, content):
        msg_type = content.get("type")
 
        if msg_type == "chat_message":
            await self.handle_chat_message(content)
        elif msg_type == "delete_message":
            await self.handle_delete_message(content)
        elif msg_type == "typing":
            await self.handle_typing(content)
        elif msg_type == "read":
            await self.handle_read()
        else:
            await self.send_json({"type": "error", "message": "Unknown message type."})
 
    async def handle_chat_message(self, content):
        text = content.get("content", "").strip()
        if not text:
            return
        if len(text) > 2000:
            await self.send_json({"type": "error", "message": "Message too long (max 2000 chars)."})
            return
 
        reply_to_id = content.get("reply_to_id")
        message = await self.create_message(text, reply_to_id)
 
        await self.channel_layer.group_send(self.group_name, {
            "type": "chat_message",
            **serialize_message(message),
        })
 
    async def handle_delete_message(self, content):
        message_id = content.get("message_id")
        if not message_id:
            return
 
        success, error = await self.soft_delete_message(message_id)
        if not success:
            await self.send_json({"type": "error", "message": error})
            return
 
        await self.channel_layer.group_send(self.group_name, {
            "type": "message_deleted",
            "message_id": message_id,
            "deleted_by": self.user.username,
        })
 
    async def handle_typing(self, content):
        await self.channel_layer.group_send(self.group_name, {
            "type": "typing",
            "username": self.user.username,
            "is_typing": bool(content.get("is_typing", False)),
        })
 
    async def handle_read(self):
        await self.mark_read()
 
    # ── Group event handlers (called by channel layer) ─────────────────────────
 
    async def chat_message(self, event):
        await self.send_json(event)
 
    async def message_deleted(self, event):
        await self.send_json(event)
 
    async def typing(self, event):
        # Don't echo back to the sender
        if event["username"] != self.user.username:
            await self.send_json(event)
 
    async def presence(self, event):
        await self.send_json(event)
 
    # ── Database helpers (run in thread pool via database_sync_to_async) ───────
 
    @database_sync_to_async
    def get_room(self):
        try:
            return Room.objects.get(slug=self.slug)
        except Room.DoesNotExist:
            return None
 
    @database_sync_to_async
    def check_membership(self):
        return Membership.objects.filter(user=self.user, room=self.room).exists()
 
    @database_sync_to_async
    def load_history(self):
        messages = get_room_history(self.room)
        return [serialize_message(m) for m in messages]
 
    @database_sync_to_async
    def create_message(self, text, reply_to_id=None):
        return save_message(
            room=self.room,
            sender=self.user,
            content=text,
            reply_to_id=reply_to_id,
        )
 
    @database_sync_to_async
    def soft_delete_message(self, message_id):
        try:
            message = Message.objects.select_related("room").get(
                id=message_id, room=self.room
            )
            delete_message(message, self.user)
            return True, None
        except Message.DoesNotExist:
            return False, "Message not found."
        except PermissionError as e:
            return False, str(e)
 
    @database_sync_to_async
    def mark_read(self):
        mark_room_read(self.user, self.room)
 
    @database_sync_to_async
    def set_online(self, status):
        from profiles.models import UserProfile
        UserProfile.objects.filter(user=self.user).update(
            is_online=status,
        )
        if not status:
            from django.utils import timezone
            UserProfile.objects.filter(user=self.user).update(last_seen=timezone.now())