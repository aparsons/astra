import logging

from django.contrib import admin
from django.utils.translation import gettext as _

from .models import OpenAIChatCompletion, OpenAIChatCompletionMessage, OpenAIChatCompletionResponse, OpenAIChatCompletionResponseChoice

logger = logging.getLogger("astra.openai_chat.admin")


@admin.action(description=_("Get selected OpenAI Chat Completion responses"))
def get_response_for_selected(modeladmin, request, queryset):
    logger.info("Getting response for selected chat completions")
    for obj in queryset:
        obj.get_response()

class OpenAIChatCompletionMessageInline(admin.TabularInline):
    model = OpenAIChatCompletionMessage
    extra = 0

class OpenAIChatCompletionAdmin(admin.ModelAdmin):
    actions = [get_response_for_selected]
    inlines = [OpenAIChatCompletionMessageInline]
    list_display = ["model", "created_at", "updated_at"]
    list_filter = ["model", "created_at", "updated_at"]
    search_fields = ["model"]

admin.site.register(OpenAIChatCompletion, OpenAIChatCompletionAdmin)

class OpenAIChatCompletionMessageAdmin(admin.ModelAdmin):
    list_display = ["chat_completion", "role", "content", "created_at", "updated_at"]
    list_filter = ["role", "created_at", "updated_at"]

admin.site.register(OpenAIChatCompletionMessage, OpenAIChatCompletionMessageAdmin)


admin.site.register(OpenAIChatCompletionResponse)

admin.site.register(OpenAIChatCompletionResponseChoice)
