import logging
import time

from arcane.engine import ArcaneEngine
from django.db import models

logger = logging.getLogger(__name__)


class ChatConversation(models.Model):
    title = models.CharField(max_length=255, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey("users.StudioUser", on_delete=models.CASCADE)
    repo = models.ForeignKey("repositories.BookmarkedRepo", on_delete=models.CASCADE)
    pr_number = models.IntegerField(null=True, blank=True)
    branch = models.CharField(max_length=255, null=True, blank=True)

    def assemble_chat_history(self):
        """Assembles a string of all messages in the conversation"""
        return "\n---\n".join([msg.history_fragment for msg in self.messages.all()])

    def continue_conversation(self, message, api_key):
        instructions = ("Read the chat history above and react + respond to the user's last message. "
                        "Only return the response, nothing else.")
        task_description = f"{self.assemble_chat_history()}\n---\nUSER:\n{message}\n---\n{instructions}"
        new_task = ArcaneEngine(api_key).create_task(self.repo.full_name, task_description,
                                                     pr_number=self.pr_number,
                                                     branch=self.branch)
        return ChatMessage.objects.create(conversation=self, message=message, task_id=new_task.id)

    def generate_title(self, api_key):
        logger.info(f"Generating title for chat {self.pk}")
        instructions = ("Read the chat history above and generate a title for the conversation. "
                        "The title should have a maximum of 4 words and start with an emoji."
                        "Only return the title, nothing else.")
        task_description = f"{self.assemble_chat_history()}\n---\n{instructions}"
        engine = ArcaneEngine(api_key)
        task = engine.create_task(self.repo.full_name, task_description)
        while task.status not in ["completed", "failed"]:
            task = engine.get_task(task.id)
            time.sleep(3)
        self.title = task.title
        self.save()

    def __str__(self):
        return self.title


class ChatMessage(models.Model):
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name="messages")
    message = models.TextField()
    result = models.TextField(null=True, blank=True)
    task_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def history_fragment(self):
        md = f"USER:\n{self.message}"
        if self.result:
            md += f"\n\n---\nASSISTANT:\n{self.result}"
        return md

    def __str__(self):
        return self.message[:50]

    class Meta:
        ordering = ["created_at"]