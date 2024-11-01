from django.contrib import admin

from .models import GitHubWebhook


class GitHubWebhookAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ['id', 'public_id', 'enabled', 'created_at', 'updated_at']
    list_display_links = ['id', 'public_id']
    list_filter = ['enabled', 'created_at', 'updated_at']
    readonly_fields = ("created_at", "updated_at")
    search_fields = ["public_id"]

admin.site.register(GitHubWebhook, GitHubWebhookAdmin)
