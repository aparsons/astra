from django.db import models


class GitHubWebhook(models.Model):
    public_id = models.CharField(max_length=255, unique=True, db_index=True)
    enabled = models.BooleanField(default=True)

    objects = models.Manager()
