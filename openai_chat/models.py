import logging

from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _

from openai import OpenAI


logger = logging.getLogger("astra.openai_chat.models")

CHAT_MODEL_CHOICES = {
    "gpt-4o": _("GPT-4o"),
    "gpt-4o-mini": _("GPT-4o Mini"),
}

# https://platform.openai.com/docs/api-reference/chat
class OpenAIChatCompletion(models.Model):
    model = models.CharField(max_length=255, choices=CHAT_MODEL_CHOICES, default="gpt-4o-mini", db_index=True, help_text=_("ID of the model to use."))
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, db_index=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _("OpenAI Chat Completion")
        verbose_name_plural = _("OpenAI Chat Completions")

    def __str__(self):
        return self.model

    def get_response(self):
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        messages = []
        for message in self.messages.all():
            messages.append({"role": message.role, "content": message.content})

        if not messages:
            logger.warning("No messages to get response in chat completion %s", self)
            return

        # https://platform.openai.com/docs/api-reference/chat/create
        chat_completion = client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        response = self.responses.create(
            model=chat_completion.model
        )

        for choice in chat_completion.choices:
            response.choices.create(
                content=choice.message.content
            )

CHAT_ROLE_CHOICES = {
    "developer": _("Developer"),
    "user": _("User"),
}

class OpenAIChatCompletionMessage(models.Model):
    chat_completion = models.ForeignKey(OpenAIChatCompletion, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=255, choices=CHAT_ROLE_CHOICES, default="user", db_index=True, help_text=_("Role of the messages author."))
    content = models.TextField(help_text=_("Content of the message."))
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, db_index=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _("OpenAI Chat Completion Message")
        verbose_name_plural = _("OpenAI Chat Completion Messages")

    def __str__(self):
        return self.content


class OpenAIChatCompletionResponse(models.Model):
    chat_completion = models.ForeignKey(OpenAIChatCompletion, on_delete=models.CASCADE, related_name="responses")
    model = models.CharField(max_length=255, db_index=True, help_text=_("The model used for the chat completion."))
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, db_index=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _("OpenAI Chat Completion Response")
        verbose_name_plural = _("OpenAI Chat Completion Responses")

    def __str__(self):
        return self.model


class OpenAIChatCompletionResponseChoice(models.Model):
    response = models.ForeignKey(OpenAIChatCompletionResponse, on_delete=models.CASCADE, related_name="choices")
    content = models.TextField(help_text=_("The contents of the message."))
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, db_index=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _("OpenAI Chat Completion Response Choice")
        verbose_name_plural = _("OpenAI Chat Completion Response Choices")

    def __str__(self):
        return self.content
