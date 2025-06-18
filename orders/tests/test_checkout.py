import pytest
from django.urls import reverse
from orders.models import CartItem

@pytest.mark.django_db
def test_checkout_creates_order(auth_client, user, mocker):
    # Mock fetch_service
    mocker.patch("orders.views.fetch_service", return_value={"name": "Foo", "price": 100.00})
    # Add item to cart
    auth_client.post(reverse("cart"), {"service_id": "svc-1"})

    response = auth_client.post(reverse("orders-checkout"))
    assert response.status_code == 201
    assert response.data["status"] == "confirmed"
    assert response.data["total_price"] == "100.00"
