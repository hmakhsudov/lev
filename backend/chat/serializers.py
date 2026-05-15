from rest_framework import serializers

from accounts.serializers import UserPublicSerializer
from real_estate.models import Property
from .models import Conversation, Message


class ListingMiniSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "id",
            "title",
            "price",
            "main_image",
            "address",
            "city",
            "district",
        ]

    def get_main_image(self, obj):
        images = obj.images or []
        if images:
            return images[0]
        first_photo = obj.gallery.first()
        return first_photo.url if first_photo else None


class MessageSerializer(serializers.ModelSerializer):
    sender = UserPublicSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "conversation", "sender", "text", "created_at", "read_at"]
        read_only_fields = ["id", "sender", "created_at", "read_at"]


class ConversationSerializer(serializers.ModelSerializer):
    listing = ListingMiniSerializer(read_only=True)
    buyer = UserPublicSerializer(read_only=True)
    agent = UserPublicSerializer(read_only=True)
    other_participant = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "listing",
            "buyer",
            "agent",
            "other_participant",
            "last_message",
            "last_message_at",
            "created_at",
            "updated_at",
        ]

    def get_other_participant(self, obj):
        request = self.context.get("request")
        if not request or not request.user:
            return None
        if request.user.id == obj.buyer_id:
            return UserPublicSerializer(obj.agent).data
        return UserPublicSerializer(obj.buyer).data

    def get_last_message(self, obj):
        text = getattr(obj, "last_message_text", None)
        created_at = getattr(obj, "last_message_created_at", None) or obj.last_message_at
        sender_id = getattr(obj, "last_message_sender_id", None)
        if not text:
            return None
        return {
            "text": text,
            "created_at": created_at,
            "sender_id": sender_id,
        }
