from django.db.models import Q, OuterRef, Subquery
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from real_estate.models import Property
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        last_message_qs = Message.objects.filter(
            conversation=OuterRef("pk")
        ).order_by("-created_at")
        queryset = (
            Conversation.objects.filter(Q(buyer=request.user) | Q(agent=request.user))
            .select_related("listing", "buyer", "agent")
            .annotate(
                last_message_text=Subquery(last_message_qs.values("text")[:1]),
                last_message_created_at=Subquery(last_message_qs.values("created_at")[:1]),
                last_message_sender_id=Subquery(last_message_qs.values("sender_id")[:1]),
            )
            .order_by("-last_message_at", "-updated_at")
        )
        serializer = ConversationSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response({"count": queryset.count(), "results": serializer.data})

    def post(self, request):
        listing_id = request.data.get("listing_id")
        if not listing_id:
            raise ValidationError({"listing_id": ["Это поле обязательно."]})
        listing = get_object_or_404(Property, pk=listing_id)
        agent = listing.created_by
        if not agent:
            raise ValidationError({"detail": "У объекта не указан агент."})
        buyer = request.user
        if buyer.id == agent.id:
            raise ValidationError({"detail": "Вы не можете писать самому себе."})
        conversation, created = Conversation.objects.get_or_create(
            listing=listing, buyer=buyer, agent=agent
        )
        serializer = ConversationSerializer(
            conversation, context={"request": request}
        )
        return Response(
            {
                "conversation": serializer.data,
                "ws_url": f"/ws/chat/{conversation.id}/",
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class ConversationDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, pk=conversation_id)
        self._assert_participant(request, conversation)
        limit = int(request.query_params.get("limit", 50))
        messages = (
            conversation.messages.select_related("sender")
            .order_by("-created_at")[:limit]
        )
        serializer = ConversationSerializer(
            conversation, context={"request": request}
        )
        messages_data = MessageSerializer(list(reversed(messages)), many=True).data
        return Response(
            {"conversation": serializer.data, "messages": messages_data}
        )

    @staticmethod
    def _assert_participant(request, conversation):
        if request.user.id not in {conversation.buyer_id, conversation.agent_id}:
            raise PermissionDenied("Доступ запрещен.")


class ConversationMessagesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, pk=conversation_id)
        self._assert_participant(request, conversation)
        limit = int(request.query_params.get("limit", 50))
        before = request.query_params.get("before")
        queryset = conversation.messages.select_related("sender").order_by("-created_at")
        if before:
            try:
                before_id = int(before)
                queryset = queryset.filter(id__lt=before_id)
            except (TypeError, ValueError):
                raise ValidationError({"before": ["Некорректный параметр before."]})
        messages = list(queryset[:limit])
        serializer = MessageSerializer(list(reversed(messages)), many=True)
        return Response({"results": serializer.data})

    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, pk=conversation_id)
        self._assert_participant(request, conversation)
        text = (request.data.get("text") or "").strip()
        if not text:
            raise ValidationError({"text": ["Сообщение не может быть пустым."]})
        message = Message.objects.create(
            conversation=conversation, sender=request.user, text=text
        )
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def _assert_participant(request, conversation):
        if request.user.id not in {conversation.buyer_id, conversation.agent_id}:
            raise PermissionDenied("Доступ запрещен.")
