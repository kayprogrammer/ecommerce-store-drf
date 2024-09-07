from django.urls import path
from . import views

urlpatterns = [
    path("apply/", views.SellersApplicationView.as_view()),
    path("products/<slug:slug>/", views.ProductsBySellerView.as_view()),
]
