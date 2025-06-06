from django.contrib import admin
from django.urls import path
from django.urls import path, include

from users.views import GoogleLoginThrottleView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/users/", include("users.urls")),
    # Handles Google login/token exchange
    path('api/auth/social/google/', GoogleLoginThrottleView.as_view(), name='google_login'), 
    # apps
    path('api/', include('orders.urls')), # for api/orders/ and /api/cart/

]
