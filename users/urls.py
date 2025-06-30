from django.urls import path, include
from allauth.account.views import ConfirmEmailView
from dj_rest_auth.registration.views import VerifyEmailView

from .views import UserDeactivateView, LoginThrottleView

urlpatterns = [
    # dj-rest-auth
    path("auth/", include("dj_rest_auth.urls")),  # default dj-rest-auth URLs
    path(
        "auth/login/", LoginThrottleView.as_view(), name="rest_login"
    ),  # override login URL
    # hendles email confirmation
    path(
        "auth/registration/account-confirm-email/<str:key>/",
        ConfirmEmailView.as_view(),
        name="account_confirm_email",
    ),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path(
        "auth/account-confirm-email/",
        VerifyEmailView.as_view(),
        name="account_confirm_email",
    ),
    # djoser
    path("djoser-auth/", include("djoser.urls")),
    path("djoser-auth/", include("djoser.urls.authtoken")),
    path("djoser-auth/", include("djoser.urls.jwt")),
    # custom
    path(
        "deactivate/<username>/",
        UserDeactivateView.as_view(),
        name="users-retrieve-deactivate",
    ),
]
