from django.conf import settings
from django.core.cache import cache
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from django.db import transaction
import requests

from .models import Cart, CartItem, Order, OrderItem, Payment
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
    PaymentSerializer,
)
from utils.cache_keys import cart_key, orders_list_key, order_detail_key, service_key

from orders.utils.email import trigger_order_confirmation_email

EXPRESS_SERVICE_URL = settings.EXPRESS_SERVICE_URL


def fetch_service(service_id):
    key = service_key(service_id)
    cached = cache.get(key)
    if cached:
        return cached

    response = requests.get(f"{EXPRESS_SERVICE_URL}/{service_id}")
    if response.status_code == 200:
        data = response.json()
        cache.set(key, data, timeout=3600)  # Cache for 1 hour
        return data

    raise ValidationError(f"Service with ID {service_id} not found.")


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        key = cart_key(request.user.id)
        cached = cache.get(key)
        if cached:
            return Response(cached)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        serialized = CartSerializer(cart).data
        cache.set(key, serialized, timeout=300)
        return Response(serialized)

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        service_id = request.data.get("service_id")

        if not service_id:
            return Response(
                {"detail": "Missing service_id"}, status=status.HTTP_400_BAD_REQUEST
            )

        if cart.items.filter(service_id=service_id).exists():
            return Response(
                {"detail": "Service already in cart."}, status=status.HTTP_409_CONFLICT
            )

        service = fetch_service(service_id)
        item = CartItem.objects.create(
            cart=cart,
            service_id=service_id,
            service_name=service.get("name"),
            price=service.get("price"),
        )
        cache.delete(cart_key(request.user.id))
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.all().delete()
            cache.delete(cart_key(request.user.id))
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)


class CartItemDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, service_id):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return Response(
                {"detail": "Cart not found."}, status=status.HTTP_404_NOT_FOUND
            )

        item = cart.items.filter(service_id=service_id).first()
        if not item:
            return Response(
                {"detail": "Item not in cart."}, status=status.HTTP_404_NOT_FOUND
            )

        item.delete()
        cache.delete(cart_key(request.user.id))
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().order_by("-ordered_at")
        return Order.objects.filter(user=user).order_by("-ordered_at")

    def list(self, request, *args, **kwargs):
        key = orders_list_key(request.user.id)
        cached = cache.get(key)
        if cached:
            return Response(cached)

        queryset = self.get_queryset()
        serialized = self.get_serializer(queryset, many=True).data
        cache.set(key, serialized, timeout=300)
        return Response(serialized)

    def retrieve(self, request, *args, **kwargs):
        order_id = kwargs.get("pk")
        key = order_detail_key(order_id)
        cached = cache.get(key)
        if cached:
            return Response(cached)

        order = self.get_object()
        serialized = self.get_serializer(order).data
        cache.set(key, serialized, timeout=300)
        return Response(serialized)

    @action(detail=True, methods=["patch"], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        order = self.get_object()
        requested_status = request.data.get("status")

        serializer = OrderStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if request.user.is_staff:
            if requested_status == "cancelled" and order.status in [
                "completed",
                "refunded",
            ]:
                return Response(
                    {"detail": f"Cannot cancel order in '{order.status}' status."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif requested_status == "completed" and order.status != "paid":
                return Response(
                    {"detail": "Can only mark paid orders as completed."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        elif order.user == request.user:
            if requested_status == "completed" and order.status != "paid":
                return Response(
                    {"detail": "Only paid orders can be marked as completed."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            elif requested_status == "cancelled" and order.status not in [
                "pending",
                "confirmed",
            ]:
                return Response(
                    {"detail": f"Cannot cancel order in '{order.status}' status."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            elif requested_status not in ["completed", "cancelled"]:
                return Response(
                    {"detail": f"Cannot change order to '{requested_status}'."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        else:
            return Response(
                {"detail": "You do not have permission to update this order."},
                status=status.HTTP_403_FORBIDDEN,
            )

        order.status = requested_status
        order.save()
        cache.delete(order_detail_key(pk))
        cache.delete(orders_list_key(request.user.id))
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def checkout(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response(
                {"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            order = Order.objects.create(user=request.user, status="confirmed")
            order_items = [
                OrderItem(
                    order=order,
                    service_id=item.service_id,
                    service_name=item.service_name,
                    price=item.price,
                )
                for item in cart.items.all()
            ]
            OrderItem.objects.bulk_create(order_items)
            order.total_price = sum(item.price for item in order_items)
            order.save()
            cart.items.all().delete()
            cache.delete(cart_key(request.user.id))

        serializer = OrderSerializer(order)
        cache.delete(orders_list_key(request.user.id))
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def pay(self, request, pk=None):
        order = self.get_object()

        if order.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You do not own this order."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if order.status != "confirmed":
            return Response(
                {"detail": "Only confirmed orders can be paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        Payment.objects.create(
            order=order,
            method=serializer.validated_data["method"],
            amount=order.total_price,
            reference_id=serializer.validated_data.get("reference_id"),
        )

        order.status = "paid"
        order.save()

        cache.delete(order_detail_key(pk))
        cache.delete(orders_list_key(order.user.id))

        order_data = {
            "items": [
                {
                    "name": item.service_name,
                    "quantity": 1,
                    "price": item.price,
                }
                for item in order.items.all()
            ],
            "total": order.total_price,
        }

        # Trigger email confirmation via Thread + Mailgun API direct call
        # Comment out for load testing
        trigger_order_confirmation_email(order.user.email, order_data)

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
