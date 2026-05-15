from django.db import models
from django.utils import timezone

from accounts.models import User
from real_estate.models import Property


class Conversation(models.Model):
    listing = models.ForeignKey(
        Property, related_name="conversations", on_delete=models.CASCADE
    )
    buyer = models.ForeignKey(
        User, related_name="buyer_conversations", on_delete=models.CASCADE
    )
    agent = models.ForeignKey(
        User, related_name="agent_conversations", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["listing", "buyer", "agent"],
                name="unique_listing_buyer_agent",
            )
        ]

    def __str__(self):
        return f"Conversation #{self.id} ({self.listing_id})"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE
    )
    sender = models.ForeignKey(User, related_name="messages", on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)
        if creating:
            Conversation.objects.filter(id=self.conversation_id).update(
                last_message_at=timezone.now(), updated_at=timezone.now()
            )

    def __str__(self):
        return f"Message #{self.id}"
