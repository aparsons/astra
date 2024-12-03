import json
import logging

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .forms import GitHubWebhookEventForm
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
def handle_github_webhook(request: HttpRequest, public_id: str) -> HttpResponse:
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

        event = request.headers.get("X-GitHub-Event")
        if not event:
            # If the X-GitHub-Event header is missing, return a 400 Bad Request response.
            logger.warning("Missing X-GitHub-Event header for webhook %s", webhook)
            return JsonResponse(data={"error": { "code": 400, "message": "Missing X-GitHub-Event header"}}, status=400)

        logger.info(f"Received {event} event for webhook {webhook}")

        if event == "installation":
            try:
                payload = json.loads(request.body)
            except json.JSONDecodeError as e:
                # If the payload is not valid JSON, return a 400 Bad Request response.
                logger.warning("Invalid JSON payload for webhook %s: %s", webhook, e)
                logger.debug(f"Received request body: {request.body.decode("utf-8")}")
                return JsonResponse(data={"error": { "code": 400, "message": "Invalid JSON payload"}}, status=400)

            action = payload.get("action")
            logger.info(f"Received {action} action for event {event} for webhook {webhook}")
            if action == "created":
                # Handle the installation created event
                pass
            elif action == "deleted":
                # Handle the installation deleted event
                pass
            else:
                logger.warning("Unsupported action %s for event %s for webhook %s", action, event, webhook)
                logger.debug(f"Received payload: {payload}")
                return JsonResponse(data={"error": { "code": 400, "message": "Unsupported action"}}, status=400)
        else:
            logger.warning("Unsupported event %s for webhook %s", event, webhook)
            logger.debug(f"Received request body: {request.body.decode("utf-8")}")
            return JsonResponse(data={"error": { "code": 400, "message": "Unsupported event"}}, status=400)

        # TODO: Validate the payload signature
        # TODO: Parse the action from the payload

        # form = GitHubWebhookEventForm()
        # form.delivery_uuid = delivery_uuid
        # form.event = event
        # form.action = action
        # form.payload = payload

        # if form.is_valid():
        #     logger.info("Valid form data for webhook %s", webhook)
        # else:
        #     for field, errors in form.errors.items():
        #         for error in errors:
        #             logger.warning("Invalid form data for webhook %s field %s: %s", webhook, field, error)

        GitHubWebhookEvent.objects.create(webhook=webhook, delivery_uuid=delivery_uuid, event=event, payload=payload)
        return JsonResponse(data={"status": "success"}, status=202)
