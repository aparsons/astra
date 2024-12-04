import json
import logging

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import GitHubWebhook, GitHubWebhookEvent

logger = logging.getLogger("astra.webhooks.views")

def index(request: HttpRequest) -> HttpResponse:
    """
    Handles the HTTP request for the index page of the webhooks.

    Returns:
        HttpResponse: A response object containing a simple greeting message.
    """
    logger.debug("Index page accessed.")
    return HttpResponse("Hello, world. You're at the webhooks index.")

# This is the view that will handle the GitHub webhook requests.
# The @csrf_exempt decorator is used to disable CSRF protection for this view.
# This is necessary because GitHub webhook requests do not include the CSRF token.
#
# https://docs.github.com/en/webhooks/using-webhooks/handling-webhook-deliveries
# https://docs.github.com/en/webhooks/webhook-events-and-payloads#delivery-headers
@csrf_exempt
def handle_github_webhook_event(request: HttpRequest, public_id: str) -> HttpResponse:
    if request.method == "POST":
        webhook = get_object_or_404(GitHubWebhook, public_id=public_id, enabled=True)

        if request.content_type != "application/json":
            # If the content type is not supported, return a 415 Unsupported Media Type response.
            logger.warning("Unsupported media type %s for webhook %s", request.content_type, webhook)
            return JsonResponse(data={"error": { "code": 415, "message": "Unsupported Media Type"}}, status=415)

        delivery_uuid = request.headers.get("X-GitHub-Delivery")
        if not delivery_uuid:
            # If the X-GitHub-Delivery header is missing, return a 400 Bad Request response.
            logger.warning("Missing X-GitHub-Delivery header for webhook %s", webhook)
            return JsonResponse(data={"error": { "code": 400, "message": "Missing X-GitHub-Delivery header"}}, status=400)

        if webhook.disallow_duplicate_deliveries:
            # If duplicate deliveries are not allowed, check if the delivery already exists.
            if GitHubWebhookEvent.objects.filter(webhook=webhook, delivery_uuid=delivery_uuid).exists():
                logger.warning(f"Duplicate delivery {delivery_uuid} for webhook {webhook}")
                return JsonResponse(data={"error": { "code": 400, "message": "Duplicate delivery"}}, status=400)

        event = request.headers.get("X-GitHub-Event")
        if not event:
            # If the X-GitHub-Event header is missing, return a 400 Bad Request response.
            logger.warning("Missing X-GitHub-Event header for webhook %s", webhook)
            return JsonResponse(data={"error": { "code": 400, "message": "Missing X-GitHub-Event header"}}, status=400)

        # TODO: Verify webhook event types

        logger.info(f"Received {event} event for webhook {webhook}")

        try:
            # TODO Add support for application/x-www-form-urlencoded
            # application/x-www-form-urlencoded will send the JSON payload as a form parameter called payload.
            # https://docs.github.com/en/webhooks/using-webhooks/creating-webhooks#creating-an-organization-webhook

            payload = json.loads(request.body)
        except json.JSONDecodeError as e:
            # If the payload is not valid JSON, return a 400 Bad Request response.
            logger.warning("Invalid JSON payload for webhook %s: %s", webhook, e)
            logger.debug(f"Received request body: {request.body.decode("utf-8")}")
            return JsonResponse(data={"error": { "code": 400, "message": "Invalid JSON payload"}}, status=400)

        if webhook.validate_deliveries:
            # TODO: Validate the payload signature
            pass

        if event == "installation":
            action = payload.get("action")
            logger.info(f"Received {action} action with {event} event for webhook {webhook}")
            if action == "created":
                # Someone installed a GitHub App on a user or organization account.
                pass
            elif action == "deleted":
                # Someone uninstalled a GitHub App from their user or organization account.
                pass
            elif action == "new_permissions_accepted":
                # Someone granted new permissions to a GitHub App.
                pass
            elif action == "suspend":
                # Someone blocked access by a GitHub App to their user or organization account.
                pass
            elif action == "unsuspend":
                # A GitHub App that was blocked from accessing a user or organization account was given access the account again.
                pass
            else:
                logger.warning(f"Unsupported action {action} with event {event} for webhook {webhook}")
                logger.debug(f"Received payload: {payload}")
                return JsonResponse(data={"error": { "code": 400, "message": "Unsupported action"}}, status=400)
        else:
            logger.warning("Unsupported event %s for webhook %s", event, webhook)
            logger.debug(f"Received request body: {request.body.decode("utf-8")}")
            return JsonResponse(data={"error": { "code": 400, "message": "Unsupported event"}}, status=400)

        GitHubWebhookEvent.objects.create(webhook=webhook, delivery_uuid=delivery_uuid, event=event, payload=payload)
        return JsonResponse(data={"status": "accepted"}, status=202)
