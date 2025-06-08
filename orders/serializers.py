from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Payment

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'service_id', 'service_name', 'price', 'added_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items']
        read_only_fields = ['user']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['service_id', 'service_name', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'ordered_at', 'status', 'items', 'total_price']
        read_only_fields = ['user', 'ordered_at']


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["pending", "confirmed", "paid", "completed", "cancelled"])


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['method', 'amount', 'reference_id', 'paid_at']
        read_only_fields = ['paid_at', 'amount']



