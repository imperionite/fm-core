import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_user_deactivate_by_self(auth_client, user):
    url = reverse("users-retrieve-deactivate", kwargs={"username": user.username})
    response = auth_client.delete(url)
    user.refresh_from_db()
    assert response.status_code == 204
    assert not user.is_active

@pytest.mark.django_db
def test_user_deactivate_by_admin(admin_client, user):
    url = reverse("users-retrieve-deactivate", kwargs={"username": user.username})
    response = admin_client.delete(url)
    user.refresh_from_db()
    assert response.status_code == 204
    assert not user.is_active
