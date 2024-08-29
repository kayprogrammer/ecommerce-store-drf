from django.urls import path
from . import views

urlpatterns = [
    path("", views.ProfileView.as_view()),
    path("shipping_addresses/", views.ShippingAddressesView.as_view()),
    path("shipping_addresses/<uuid:id>/", views.ShippingAddressView.as_view()),
    path("orders/", views.OrdersView.as_view()),
]
