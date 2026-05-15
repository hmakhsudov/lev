from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        user = self.scope.get("user")
        if not user or not getattr(user, "is_authenticated", False):
            await self.close(code=4401)
            return
        conversation = await self._get_conversation()
        if not conversation:
            await self.close(code=4403)
            return
        if user.id not in {conversation.buyer_id, conversation.agent_id}:
            await self.close(code=4403)
            return
        self.group_name = f"chat_{self.conversation_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        msg_type = content.get("type")
        if msg_type == "message":
            await self._handle_message(content)
            return
        if msg_type == "read":
            await self.send_json({"type": "error", "detail": "Чтение не поддерживается."})
            return
        await self.send_json({"type": "error", "detail": "Неизвестный тип события."})

    async def _handle_message(self, content):
        text = (content.get("text") or "").strip()
        if not text:
            await self.send_json({"type": "error", "detail": "Сообщение не может быть пустым."})
            return
        message = await self._create_message(text)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "message": message,
            },
        )

    async def chat_message(self, event):
        await self.send_json({"type": "message", "message": event["message"]})

    @database_sync_to_async
    def _get_conversation(self):
        from .models import Conversation

        try:
            return Conversation.objects.get(id=self.conversation_id)
        except Conversation.DoesNotExist:
            return None

    @database_sync_to_async
    def _create_message(self, text):
        from accounts.serializers import UserPublicSerializer
        from .models import Message

        message = Message.objects.create(
            conversation_id=self.conversation_id,
            sender=self.scope["user"],
            text=text,
        )
        return {
            "id": message.id,
            "conversation_id": message.conversation_id,
            "sender": UserPublicSerializer(message.sender).data,
            "text": message.text,
            "created_at": message.created_at.isoformat(),
        }
