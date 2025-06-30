from django.urls import path
from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import CartView, CartItemDeleteView, OrderViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()
router.register("orders", OrderViewSet, basename="orders")

urlpatterns = [
    path("cart/", CartView.as_view(), name="cart"),
    path(
        "cart/<str:service_id>/", CartItemDeleteView.as_view(), name="cart-item-delete"
    ),
]

urlpatterns += router.urls
