from django.db import models
from django.conf import settings


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    service_id = models.CharField(max_length=255, db_index=True)  # frequent filtering by service_id in cart
    service_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service_name} (${self.price})"


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    ordered_at = models.DateTimeField(
        auto_now_add=True, db_index=True
    )  # 👈 for ordering by date
    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("paid", "Paid"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
        db_index=True,  # 👈 for frequent filtering by status
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        indexes = [
            models.Index(
                fields=["user", "status"]
            ),  # 👈 optional composite index: user + status
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    service_id = models.CharField(max_length=255, db_index=True)  # useful for reporting / analytics
    service_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Payment(models.Model):
    PAYMENT_METHODS = [
        ("maya", "Maya"),
        ("card", "Card"),
        ("paypal", "PayPal"),
    ]

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="payment"
    )
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    paid_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,  # for external reconciliation lookups
    )

    def __str__(self):
        return f"{self.method.upper()} payment for Order #{self.order.id}"
