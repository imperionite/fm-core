import pytest


@pytest.mark.django_db
def test_add_service_to_cart(auth_client, mocker):
    mock_service = {"name": "Premium Plan", "price": 999.99}
    mocker.patch("orders.views.fetch_service", return_value=mock_service)

    response = auth_client.post("/api/cart/", {"service_id": "abc123"}, format="json")

    assert response.status_code == 201
    assert response.data["service_name"] == "Premium Plan"


@pytest.mark.django_db
def test_get_cart_contents(auth_client):
    response = auth_client.get("/api/cart/")
    assert response.status_code == 200
    assert "items" in response.data

# For future reference
# @pytest.mark.django_db
# def test_clear_cart(auth_client):
#     response = auth_client.delete("/api/cart/")
#     assert response.status_code in (204, 200)
