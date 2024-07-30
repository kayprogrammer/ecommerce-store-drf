from django.urls import path
from . import views

urlpatterns = [
    path("google/<str:token>/", views.GoogleAuthView.as_view()),
    path("facebook/<str:token>/", views.FacebookAuthView.as_view()),
]