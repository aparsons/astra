from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('github/<slug:public_id>/handle', views.handle_github_webhook, name='handle_github_webhook'),
]
