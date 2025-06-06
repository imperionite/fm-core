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

from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, OrderStatusUpdateSerializer
from users.permissions import IsOwnerOrAdmin, IsEmailVerified

EXPRESS_SERVICE_URL = settings.EXPRESS_SERVICE_URL

def fetch_service(service_id):
    cache_key = f"service_{service_id}"
    cached_service = cache.get(cache_key)
    if cached_service:
        return cached_service

    response = requests.get(f"{EXPRESS_SERVICE_URL}/{service_id}")
    if response.status_code == 200:
        service_data = response.json()
        cache.set(cache_key, service_data, timeout=3600)  # Cache for 1 hour
        return service_data
    raise ValidationError(f"Service with ID {service_id} not found.")


class CartView(APIView):
    permission_classes = [IsAuthenticated, IsEmailVerified]

    def get(self, request):
        cache_key = f"cart_user_{request.user.id}"
        cached_cart = cache.get(cache_key)
        if cached_cart:
            return Response(cached_cart)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        cache.set(cache_key, serializer.data, timeout=300)  # Cache for 5 minutes
        return Response(serializer.data)

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        service_id = request.data.get("service_id")

        if not service_id:
            return Response({"detail": "Missing service_id"}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent duplicates
        if cart.items.filter(service_id=service_id).exists():
            return Response({"detail": "Service already in cart."}, status=status.HTTP_409_CONFLICT)

        service = fetch_service(service_id)
        item = CartItem.objects.create(
            cart=cart,
            service_id=service_id,
            service_name=service.get("name"),
            price=service.get("price"),
        )
        cache_key = f"cart_user_{request.user.id}"
        cache.delete(cache_key)
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.all().delete()
            cache_key = f"cart_user_{request.user.id}"
            cache.delete(cache_key)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)


class CartItemDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, service_id):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return Response({"detail": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

        item = cart.items.filter(service_id=service_id).first()
        if not item:
            return Response({"detail": "Item not in cart."}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsEmailVerified]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        # Staff sees all orders; regular users see only their own
        base_qs = Order.objects.all() if user.is_staff else Order.objects.filter(user=user)
        return base_qs.order_by('-ordered_at')
    
    def list(self, request, *args, **kwargs):
        user = request.user
        cache_key = f"orders_list_user_{user.id}"
        cached_orders = cache.get(cache_key)
        if cached_orders:
            return Response(cached_orders)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=300)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        cache_key = f"order_{order_id}"
        cached_order = cache.get(cache_key)
        if cached_order:
            return Response(cached_order)

        order = self.get_object()
        serializer = self.get_serializer(order)
        cache.set(cache_key, serializer.data, timeout=300)
        return Response(serializer.data)

    # Users can only update their own order from confirmed → completed; Admin can update any status
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        order = self.get_object()

        # Admins can do anything
        if request.user.is_staff:
            pass
        # Regular user can only mark their own orders as completed
        elif order.user != request.user:
            return Response(
                {"detail": "You do not have permission to update this order."},
                status=status.HTTP_403_FORBIDDEN
            )
        elif request.data.get("status") != "completed" or order.status != "confirmed":
            return Response(
                {"detail": "You can only mark your confirmed order as completed."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = OrderStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order.status = serializer.validated_data['status']
        order.save()
        # Invalidate cache for this order after update
        cache_key = f"order_{pk}"
        cache.delete(cache_key)
        # Also invalidate orders list cache for user
        cache.delete(f"orders_list_user_{request.user.id}")
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

    # Update your checkout() to auto-set status to "confirmed" after creation
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def checkout(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response(
                {"detail": "Cart is empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Create order with status='confirmed'
            order = Order.objects.create(user=request.user, status="confirmed")

            # Add OrderItems
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

            # Calculate total price
            order.total_price = sum(item.price for item in order_items)
            order.save()

            # Clear cart
            cart.items.all().delete()

        serializer = OrderSerializer(order)
        # Invalidate orders list cache for user after checkout
        cache.delete(f"orders_list_user_{request.user.id}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)


