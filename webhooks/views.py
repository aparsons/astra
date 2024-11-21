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
def handle_github_webhook(request: HttpRequest, public_id: str) -> HttpResponse:
    if request.method == "POST":
        webhook = get_object_or_404(GitHubWebhook, public_id=public_id, enabled=True)

        delivery_uuid = request.headers["X-GitHub-Delivery"]
        if not delivery_uuid:
            # If the X-GitHub-Delivery header is missing, return a 400 Bad Request response.
            logger.warning("Missing X-GitHub-Delivery header for webhook %s", webhook)
            return JsonResponse(data={"error": { "code": 400, "message": "Missing X-GitHub-Delivery header"}}, status=400)

        event = request.headers["X-GitHub-Event"]
        if not event:
            # If the X-GitHub-Event header is missing, return a 400 Bad Request response.
            logger.warning("Missing X-GitHub-Event header for webhook %s", webhook)
            return JsonResponse(data={"error": { "code": 400, "message": "Missing X-GitHub-Event header"}}, status=400)

        logger.info(f"Received {event} event for webhook {webhook}")

        payload = request.body

        logger.debug(f"Received payload: {payload}")

        GitHubWebhookEvent.objects.create(webhook=webhook, delivery_uuid=delivery_uuid, event=event, payload=payload)
        return JsonResponse(data={"status": "success"}, status=202)
