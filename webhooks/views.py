import logging

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import GitHubWebhook

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
@csrf_exempt
def handle_github_webhook(request: HttpRequest, public_id: str) -> HttpResponse:
    if request.method == "POST":
        webhook = get_object_or_404(GitHubWebhook, public_id=public_id, enabled=True)
        payload = request.body
        logger.info("Received webhook for %s: %s", webhook, payload)
        return JsonResponse({"status": "success"})
