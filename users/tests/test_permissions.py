# users/tests/test_permissions.py
import pytest
from users.permissions import IsOwnerOrAdmin
from rest_framework.test import APIRequestFactory
from model_bakery import baker

@pytest.mark.django_db
def test_is_owner_or_admin_for_owner(user):
    factory = APIRequestFactory()
    request = factory.get("/")
    request.user = user
    perm = IsOwnerOrAdmin()
    assert perm.has_permission(request, None)
    assert perm.has_object_permission(request, None, user)

@pytest.mark.django_db
def test_is_owner_or_admin_for_admin(admin_user, user):
    factory = APIRequestFactory()
    request = factory.get("/")
    request.user = admin_user
    perm = IsOwnerOrAdmin()
    assert perm.has_permission(request, None)
    assert perm.has_object_permission(request, None, user)

@pytest.mark.django_db
def test_is_owner_or_admin_denied_for_other_user(user):
    other_user = baker.make("users.User", is_superuser=False, is_staff=False)
    factory = APIRequestFactory()
    request = factory.get("/")
    request.user = other_user
    perm = IsOwnerOrAdmin()
    assert not perm.has_object_permission(request, None, user)
