from django.core.management.base import BaseCommand

from webhooks.models import GitHubWebhook


class Command(BaseCommand):
    help = "Rotate encryption keys"

    def handle(self, *args, **options):


        # fields = GitHubWebhook._meta.get_fields()
        # for field in fields:
        #     if hasattr(field, "rotate"):
        #         self.stdout.write(f"Rotating encryption keys for field {field.name}")
        #         field.rotate()

        # for webhook in GitHubWebhook.objects.all():
        #     self.stdout.write(f"Rotating encryption keys for webhook {webhook.pk}")
        #     webhook.client_id.rotate()

        self.stdout.write("This command is not implemented yet")
