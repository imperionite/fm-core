# Sets up fixtures shared across all test modules
import pytest
from model_bakery import baker
from rest_framework.test import APIClient


@pytest.fixture
def user(db):
    return baker.make("users.User", is_active=True)


@pytest.fixture
def admin_user(db):
    return baker.make("users.User", is_active=True, is_staff=True)


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(user, client):
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_client(admin_user, client):
    client.force_authenticate(user=admin_user)
    return client
