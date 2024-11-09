from django.core.management.base import BaseCommand

from cryptography.fernet import Fernet

class Command(BaseCommand):
    help = "Generate encryption key"

    def handle(self, *args, **options):
        self.stdout.write("Generating encryption key")
        key = Fernet.generate_key().decode("utf-8")
        self.stdout.write(self.style.SUCCESS(f"Generated key: {key}"))
