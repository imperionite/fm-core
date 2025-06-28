import pytest
from django.urls import reverse
from orders.models import Payment

@pytest.mark.django_db
def test_order_payment_flow(auth_client, user, mocker):
    # Mock external service
    mocker.patch("orders.views.fetch_service", return_value={"name": "X", "price": 200})
    
    # Mock email thread trigger
    mock_email_trigger = mocker.patch("orders.views.trigger_order_confirmation_email")

    # Add to cart
    auth_client.post(reverse("cart"), {"service_id": "svc-xyz"})

    # Checkout
    checkout_resp = auth_client.post(reverse("orders-checkout"))
    order_id = checkout_resp.data["id"]

    # Pay
    pay_resp = auth_client.post(
        reverse("orders-pay", kwargs={"pk": order_id}),
        data={"method": "maya"}
    )

    # Validate response
    assert pay_resp.status_code == 200
    assert pay_resp.data["status"] == "paid"
    assert Payment.objects.filter(order_id=order_id).exists()
    mock_email_trigger.assert_called_once()
