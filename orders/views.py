from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
import requests

from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer
from users.permissions import IsOwnerOrAdmin, IsEmailVerified

EXPRESS_SERVICE_URL = settings.EXPRESS_SERVICE_URL

def fetch_service(service_id):
    response = requests.get(f"{EXPRESS_SERVICE_URL}/{service_id}")
    if response.status_code == 200:
        return response.json()
    raise ValidationError(f"Service with ID {service_id} not found.")


class CartView(APIView):
    permission_classes = [IsAuthenticated, IsEmailVerified]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
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
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.all().delete()
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
    permission_classes = [IsAuthenticated, IsEmailVerified, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.all() if user.is_staff else Order.objects.filter(user=user)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        if not request.user.is_staff:
            return Response({"detail": "Only admins can update order status."}, status=403)

        order = self.get_object()
        new_status = request.data.get("status")
        if new_status not in ["pending", "confirmed", "completed", "cancelled"]:
            return Response({"detail": "Invalid status."}, status=400)

        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data)

