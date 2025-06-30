from django.contrib import admin
from .models import Order, Cart, CartItem, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "ordered_at", "status")
    list_filter = ("status", "ordered_at")
    search_fields = ("user__username", "id")
    ordering = ("-ordered_at",)
    readonly_fields = ("ordered_at",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    search_fields = ("user__username",)
    readonly_fields = ("created_at",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "service_name", "price", "added_at")
    search_fields = ("cart__user__username", "service_name")
    readonly_fields = ("added_at",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "service_name", "price")
    search_fields = ("order__user__username", "service_name")
