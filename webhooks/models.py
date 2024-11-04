from django.db import models

from encryption.fields import EncryptedCharField, EncryptedTextField

class GitHubWebhook(models.Model):
    public_id = models.SlugField(unique=True, db_index=True)
    client_id = EncryptedTextField()
    client_secret = EncryptedCharField(max_length=255)
    enabled = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, db_index=True)

    objects = models.Manager()

    class Meta:
        get_latest_by = "updated_at"
        ordering = ["-updated_at"]
        verbose_name = "GitHub Webhook"
        verbose_name_plural = "GitHub Webhooks"

    def __str__(self):
        return self.public_id
