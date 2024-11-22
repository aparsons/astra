from django import forms


class GitHubWebhookEventForm(forms.Form):
    delivery_uuid = forms.UUIDField()
    event = forms.CharField(max_length=255)
    action = forms.CharField(max_length=255)
    payload = forms.JSONField()
