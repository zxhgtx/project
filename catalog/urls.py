from django.urls import path

from . import views

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("about/", views.about, name="about"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:pk>/", views.update_cart, name="update_cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("order/<int:pk>/success/", views.order_success, name="order_success"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
]
