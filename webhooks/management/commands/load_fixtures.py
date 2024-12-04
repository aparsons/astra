import os

from django.core.management.base import BaseCommand

from webhooks.models import GitHubWebhook


class Command(BaseCommand):
    help = "Load development fixtures"

    def handle(self, *args, **options):
        self.stdout.write("Loading development fixtures")

        secret_token = "test-secret-token"

        django_github_webhook_secret_token_file = ".django_github_webhook_secret_token_file"
        if os.path.isfile(django_github_webhook_secret_token_file):
            self.stdout.write(f"Reading secret_token from {django_github_webhook_secret_token_file}")
            with open(django_github_webhook_secret_token_file, "r", encoding="utf-8") as f:
                secret_token = f.read().strip()

        webhook = GitHubWebhook.objects.create(
            public_id="123",
            client_id="test-client-id",
            secret_token=secret_token,
            # Allow duplicate deliveries for testing purposes
            disallow_duplicate_deliveries=False,
        )

        self.stdout.write(self.style.SUCCESS(f"Created GitHub webhook: {webhook}"))
