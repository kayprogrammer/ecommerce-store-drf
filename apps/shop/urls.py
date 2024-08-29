from django.urls import path
from . import views

urlpatterns = [
    path("products/", views.ProductsView.as_view()),
    path("products/<slug:slug>/", views.ProductView.as_view()),
    path("categories/", views.CategoriesView.as_view()),
    path("categories/<slug:slug>/", views.ProductsByCategoryView.as_view()),
    path("wishlist/", views.WishlistView.as_view()),
    path("wishlist/<slug:slug>/", views.ToggleWishlistView.as_view()),
    path("cart/", views.CartView.as_view()),
    path("checkout/", views.CheckoutView.as_view()),
    path("paystack-webhook/", views.paystack_webhook),
    path("paypal-webhook/", views.paypal_webhook),
]
