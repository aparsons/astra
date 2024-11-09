from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction

from encryption.fields import EncryptedTextField
from django.conf import settings


class Command(BaseCommand):
    help = "Rotate encryption keys"

    def handle(self, *args, **options):
        # Check if encryption key fallbacks are set in settings
        if not hasattr(settings, 'ENCRYPTION_KEY_FALLBACKS') or not settings.ENCRYPTION_KEY_FALLBACKS:
            self.stdout.write(self.style.ERROR("No encryption key fallbacks found in settings"))
            return

         # Get all models with EncryptedTextField fields
        models_with_encrypted_fields = {
            model for model in apps.get_models()
            if any(isinstance(field, EncryptedTextField) for field in model._meta.get_fields())
        }

        # Rotate encryption keys for each model
        for model in models_with_encrypted_fields:
            self.stdout.write(f"Rotating encryption keys for model {model._meta.verbose_name}")

            # Get all EncryptedTextField fields on the model
            encrypted_fields_on_model = [field for field in model._meta.get_fields() if isinstance(field, EncryptedTextField)]
            self.stdout.write(f"Found {len(encrypted_fields_on_model)} encrypted fields on model {model._meta.verbose_name}")

            # Rotate encryption keys for each instance
            with transaction.atomic():
                for instance in model.objects.all():
                    self.stdout.write(f"Rotating encryption keys for instance {instance.pk}")
                    # Re-saving the instance is crude but effective.
                    # A more efficient approach would be to update the field values directly in the database.
                    # However, this approach is more complex and error-prone.
                    # The current approach is simple and works well for small datasets.
                    # For large datasets, consider using a more efficient approach.
                    # For example, you could use the Django ORM to update the field values directly in the database.

                    # TODO: Implement a more efficient approach for large datasets
                    # TODO: Implement a rotation that doesn't cause the updated_at field to be updated
                    instance.save()

            self.stdout.write(self.style.SUCCESS(f"Encryption keys rotated for model {model._meta.verbose_name}"))

        self.stdout.write(self.style.SUCCESS("Encryption keys rotated successfully"))
