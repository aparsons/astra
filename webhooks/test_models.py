from django.test import TestCase
from .models import GitHubWebhook

class GitHubWebhookModelTest(TestCase):

    def test_create_github_webhook(self):
        webhook = GitHubWebhook.objects.create(public_id="test_id")
        self.assertEqual(webhook.public_id, "test_id")
        self.assertTrue(webhook.enabled)

    def test_unique_public_id(self):
        GitHubWebhook.objects.create(public_id="unique_id")
        with self.assertRaises(Exception):
            GitHubWebhook.objects.create(public_id="unique_id")

    def test_default_enabled(self):
        webhook = GitHubWebhook.objects.create(public_id="another_test_id")
        self.assertTrue(webhook.enabled)
