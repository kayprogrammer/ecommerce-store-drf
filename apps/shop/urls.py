from django.urls import path
from . import views

urlpatterns = [
    path("products/", views.ProductsView.as_view()),
    path("products/<slug:slug>/", views.ProductView.as_view()),
    path("categories/", views.CategoriesView.as_view()),
]
