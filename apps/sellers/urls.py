from django.urls import path
from . import views

urlpatterns = [
    path("apply/", views.SellersApplicationView.as_view()),
    path("products/<slug:slug>/", views.ProductsBySellerView.as_view()),
    path("products/", views.ProductCreateView.as_view()),
    path("orders/", views.OrdersView.as_view()),
]
