from django.urls import path
from . import views

urlpatterns = [
    path("", views.ProfileView.as_view()),
]
