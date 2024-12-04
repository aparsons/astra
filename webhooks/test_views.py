import json
import uuid

from django.test import Client, TestCase

from .models import GitHubWebhook


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index(self):
        response = self.client.get("/webhooks/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello, world. You're at the webhooks index.")

    def test_handle_github_webhook_event(self):
        public_id = "123456"
        url = f"/webhooks/github/{public_id}/handle"
        delivery_uuid = str(uuid.uuid4())

        # Test for 404 when webhook does not exist
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        # Test for 404 when webhook exists but is not enabled
        webhook = GitHubWebhook.objects.create(public_id=public_id, enabled=False)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        webhook.enabled = True
        webhook.save()

        # Test for 415 when media type is not application/json
        response = self.client.post(url, data=json.dumps({}), content_type="text/plain")
        self.assertEqual(response.status_code, 415)
        self.assertEqual(response.json(), {"error": {"code": 415, "message": "Unsupported Media Type"}})

        # Test for 400 when X-GitHub-Delivery header is missing
        response = self.client.post(url, data=json.dumps({}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": {"code": 400, "message": "Missing X-GitHub-Delivery header"}})

        # Test for 400 when X-GitHub-Event header is missing
        headers = {"X-GitHub-Delivery": delivery_uuid}
        response = self.client.post(url, data=json.dumps({}), content_type="application/json", headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": {"code": 400, "message": "Missing X-GitHub-Event header"}})

        # Test for 400 when event is unsupported
        headers["X-GitHub-Event"] = "unsupported"
        response = self.client.post(url, data=json.dumps({}), content_type="application/json", headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": {"code": 400, "message": "Unsupported event"}})

        # Test for 400 when event is "installation" but JSON payload is invalid
        headers["X-GitHub-Event"] = "installation"
        response = self.client.post(url, data="invalid", content_type="application/json", headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": {"code": 400, "message": "Invalid JSON payload"}})

        # Test for 400 when event is "installation" but action is unsupported
        response = self.client.post(url, data=json.dumps({"action": "unsupported"}), content_type="application/json", headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": {"code": 400, "message": "Unsupported action"}})

        # Test for 202 when event is "installation" and action is "created"
        response = self.client.post(url, data=json.dumps({"action": "created"}), content_type="application/json", headers=headers)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json(), {"status": "accepted"})

        # Test for 202 when event is "installation" and action is "deleted"
        response = self.client.post(url, data=json.dumps({"action": "deleted"}), content_type="application/json", headers=headers)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json(), {"status": "accepted"})
