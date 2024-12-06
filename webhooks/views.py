import json
import logging
from urllib.parse import parse_qs

from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, JsonResponse
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
        # TODO Verify webhook event types

        logger.info(f"Received {event} event for webhook {webhook}")
        logger.debug(f"Received request body: {request.body.decode("utf-8")}")

        # If the content type is "application/x-www-form-urlencoded", extract the payload from the "payload" parameter.
        if request.content_type == "application/x-www-form-urlencoded":
            try:
                decoded_payload = parse_qs(request.body.decode("utf-8"), strict_parsing=True)
            except ValueError as e:
                logger.warning(f"Invalid URL-encoded payload for webhook {webhook}: {e}")
                return JsonResponse(data={"error": { "code": 400, "message": "Invalid URL-encoded payload"}}, status=400)

            body = decoded_payload.get("payload")[0]
            # TODO Add handling for if the payload isn't present in the request body
            body = body.replace("'", '"')
            # TODO Replacing single quotes with double quotes is a workaround for the URL-encoded payload.
        # If the content type is "application/json", extract the payload from the request body.
        elif request.content_type == "application/json":
            body = request.body.decode("utf-8")
        else:
            # If the content type is not supported, return a 415 Unsupported Media Type response.
            logger.warning("Unsupported media type %s for webhook %s", request.content_type, webhook)
            return JsonResponse(data={"error": { "code": 415, "message": "Unsupported media type"}}, status=415)

        # Parse the payload as JSON.
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as e:
            # If the payload is not valid JSON, return a 400 Bad Request response.
            logger.warning(f"Invalid JSON payload for webhook {webhook}: {e}")
            logger.debug(f"Received invalid JSON request body: {body}")
            return JsonResponse(data={"error": { "code": 400, "message": "Invalid JSON payload"}}, status=400)

        if webhook.validate_deliveries:
            # TODO Validate the payload signature
            pass

        # Get the delivery from the payload using the delivery UUID.
        delivery = payload.get(delivery_uuid)
        if not delivery:
            logger.warning(f"Delivery {delivery_uuid} not found in payload for webhook {webhook}")
            return JsonResponse(data={"error": { "code": 400, "message": "X-GitHub-Delivery header must match payload"}}, status=400)

        if event == "installation":
            action = delivery.get("action")
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
    return HttpResponseNotFound()
