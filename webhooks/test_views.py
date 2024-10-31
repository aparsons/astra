from django.test import Client, TestCase

from .models import GitHubWebhook


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index(self):
        response = self.client.get("/webhooks/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello, world. You're at the webhooks index.")

    def test_handle_github_webhook(self):
        # Test for 404 when webhook does not exist
        response = self.client.post("/webhooks/github/123456/handle")
        self.assertEqual(response.status_code, 404)

        # Test for 404 when webhook exists but is not enabled
        webhook = GitHubWebhook.objects.create(public_id="123456", enabled=False)
        response = self.client.post(f"/webhooks/github/{webhook.public_id}/handle")
        self.assertEqual(response.status_code, 404)

        # Test for successful handling of webhook
        webhook.enabled = True
        webhook.save()
        response = self.client.post(f"/webhooks/github/{webhook.public_id}/handle", data={"key": "value"}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success"})
