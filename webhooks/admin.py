from collections.abc import Callable
from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .models import GitHubWebhook, GitHubWebhookEvent


class GitHubWebhookAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ['id', 'public_id', 'enabled', 'created_at', 'updated_at']
    list_display_links = ['id', 'public_id']
    list_filter = ['enabled', 'created_at', 'updated_at']
    readonly_fields = ("created_at", "updated_at")
    search_fields = ["public_id"]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
       return super().get_queryset(request).defer("client_id", "secret_token")

admin.site.register(GitHubWebhook, GitHubWebhookAdmin)


class GitHubWebhookEventAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ['id', 'webhook', 'event', 'created_at', 'updated_at']
    list_display_links = ['id', 'webhook']
    list_filter = ['event', 'created_at', 'updated_at']
    readonly_fields = ("created_at", "updated_at")
    search_fields = ["webhook__public_id", "event"]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
       return super().get_queryset(request).select_related("webhook")

admin.site.register(GitHubWebhookEvent)
