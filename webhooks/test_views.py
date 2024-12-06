import json
from urllib.parse import urlencode
import uuid

from django.test import Client, TestCase

from .models import GitHubWebhook, GitHubWebhookEvent


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index(self):
        response = self.client.get("/webhooks/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello, world. You're at the webhooks index.")


class HandleGitHubWebhookEventTest(TestCase):
    def setUp(self):
        self.client = Client()

    public_id = "test-public-id"
    url = f"/webhooks/github/{public_id}/handle"

    def test_handle_github_webhook_event_get_returns_404(self):
        response = self.client.get("/webhooks/github/123456/handle")
        self.assertEqual(response.status_code, 404)

    def test_handle_github_webhook_event_public_id_not_found_returns_404(self):
        response = self.client.post("/webhooks/github/123456/handle")
        self.assertEqual(response.status_code, 404)

    def test_handle_github_webhook_event_disabled_returns_404(self):
        GitHubWebhook.objects.create(public_id=self.public_id, enabled=False)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)

    def test_handle_github_webhook_event_missing_delivery_header_returns_400(self):
        GitHubWebhook.objects.create(public_id=self.public_id)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": {"code": 400, "message": "Missing X-GitHub-Delivery header"}})

    def test_handle_github_webhook_event_duplicate_delivery_returns_400(self):
        webhook = GitHubWebhook.objects.create(public_id=self.public_id)
        delivery_uuid = str(uuid.uuid4())
        GitHubWebhookEvent.objects.create(webhook=webhook, delivery_uuid=delivery_uuid, event="test", payload={})
        headers = {"X-GitHub-Delivery": delivery_uuid}
        response = self.client.post(self.url, data=json.dumps({}), content_type="application/json", headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": {"code": 400, "message": "Duplicate delivery"}})

    def test_handle_github_webhook_event_missing_event_header_returns_400(self):
        GitHubWebhook.objects.create(public_id=self.public_id)
        headers = {"X-GitHub-Delivery": str(uuid.uuid4())}
        response = self.client.post(self.url, data=json.dumps({}), content_type="application/json", headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": {"code": 400, "message": "Missing X-GitHub-Event header"}})

    def test_handle_github_webhook_event_invalid_url_encoded_payload_returns_400(self):
        GitHubWebhook.objects.create(public_id=self.public_id)
        headers = {"X-GitHub-Delivery": str(uuid.uuid4()), "X-GitHub-Event": "test"}
        response = self.client.post(self.url, data="invalid", content_type="application/x-www-form-urlencoded", headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": {"code": 400, "message": "Invalid URL-encoded payload"}})

    def test_handle_github_webhook_event_unsupported_media_type_returns_415(self):
        GitHubWebhook.objects.create(public_id=self.public_id)
        headers = {"X-GitHub-Delivery": str(uuid.uuid4()), "X-GitHub-Event": "unsupported"}
        response = self.client.post(self.url, data=json.dumps({}), content_type="text/plain", headers=headers)
        self.assertEqual(response.status_code, 415)
        self.assertEqual(response.json(), {"error": {"code": 415, "message": "Unsupported media type"}})

    def test_handle_github_webhook_event_invalid_json_payload_returns_400(self):
        GitHubWebhook.objects.create(public_id=self.public_id)
        headers = {"X-GitHub-Delivery": str(uuid.uuid4()), "X-GitHub-Event": "test"}
        response = self.client.post(self.url, data="invalid", content_type="application/json", headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": {"code": 400, "message": "Invalid JSON payload"}})

    def test_handle_github_webhook_event_payload_without_delivery_uuid_returns_400(self):
        GitHubWebhook.objects.create(public_id=self.public_id)
        headers = {"X-GitHub-Delivery": str(uuid.uuid4()), "X-GitHub-Event": "test"}
        response = self.client.post(self.url, data=json.dumps({}), content_type="application/json", headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": {"code": 400, "message": "X-GitHub-Delivery header must match payload"}})

    def test_handle_github_webhook_event_unsupported_event_returns_400(self):
        GitHubWebhook.objects.create(public_id=self.public_id)
        delivery_uuid = str(uuid.uuid4())
        headers = {"X-GitHub-Delivery": delivery_uuid, "X-GitHub-Event": "unsupported"}
        data = {
            delivery_uuid: {
                "action": "created"
            }
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json", headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": {"code": 400, "message": "Unsupported event"}})

    def test_handle_github_webhook_event_installation_created_json_returns_202(self):
        GitHubWebhook.objects.create(public_id=self.public_id)
        delivery_uuid = str(uuid.uuid4())
        headers = {"X-GitHub-Delivery": delivery_uuid, "X-GitHub-Event": "installation"}
        data = {
            delivery_uuid: {
                "action": "created"
            }
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json", headers=headers)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json(), {"status": "accepted"})

    # python manage.py test webhooks.test_views.HandleGitHubWebhookEventTest.test_handle_github_webhook_event_installation_created_form_returns_202
    def test_handle_github_webhook_event_installation_created_form_returns_202(self):
        GitHubWebhook.objects.create(public_id=self.public_id)
        delivery_uuid = str(uuid.uuid4())
        headers = {"X-GitHub-Delivery": delivery_uuid, "X-GitHub-Event": "installation"}
        data = {
            "payload": {
                delivery_uuid: {
                    "action": "created"
                }
            }
        }
        encoded_data = urlencode(data)
        response = self.client.post(self.url, data=encoded_data, content_type="application/x-www-form-urlencoded", headers=headers)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json(), {"status": "accepted"})
