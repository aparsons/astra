from django.db import models
from django.utils.translation import gettext as _

from encryption.fields import EncryptedTextField

class GitHubWebhook(models.Model):
    public_id = models.SlugField(unique=True, db_index=True)
    client_id = EncryptedTextField()
    secret_token = EncryptedTextField()
    enabled = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, db_index=True)

    objects = models.Manager()

    class Meta:
        get_latest_by = "updated_at"
        ordering = ["-updated_at"]
        verbose_name = _("GitHub Webhook")
        verbose_name_plural = _("GitHub Webhooks")

    def __str__(self):
        return self.public_id


class GitHubWebhookEvent(models.Model):
    webhook = models.ForeignKey(GitHubWebhook, on_delete=models.CASCADE)
    delivery_uuid = models.UUIDField(unique=True, db_index=True, help_text=_("A globally unique identifier (GUID) to identify the event."))
    event = models.CharField(max_length=255, db_index=True, help_text=_("The name of the event that triggered the delivery."))
    action = models.CharField(max_length=255, blank=True, db_index=True)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, db_index=True)

    objects = models.Manager()

    class Meta:
        get_latest_by = "updated_at"
        ordering = ["-updated_at"]
        verbose_name = _("GitHub Webhook Event")
        verbose_name_plural = _("GitHub Webhook Events")

    def __str__(self):
        return f"{self.webhook} - {self.event}"
