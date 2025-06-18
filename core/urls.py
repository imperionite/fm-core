from django.contrib import admin
from django.urls import path
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from users.views import GoogleLoginThrottleView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/users/", include("users.urls")),
    # Handles Google login/token exchange
    path('api/auth/social/google/', GoogleLoginThrottleView.as_view(), name='google_login'), 
    # apps
    path('api/', include('orders.urls')), # for api/orders/ and /api/cart/
    # api docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

]
