from django.urls import path
from . import views

urlpatterns = [
    path("google/", views.GoogleAuthView.as_view()),
    path("facebook/", views.FacebookAuthView.as_view()),
    path("refresh/", views.RefreshTokensView.as_view()),
    path("logout/", views.LogoutView.as_view()),
]
