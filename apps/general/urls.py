from django.urls import path

from . import views

urlpatterns = [
    path("site-detail/", views.SiteDetailView.as_view()),
    path("subscribe/", views.SubscribeView.as_view()),
    path("message/", views.MessageView.as_view()),
]
