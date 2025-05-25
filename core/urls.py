from django.contrib import admin
from django.urls import path
from django.urls import path, include

from users.views import GoogleLogin

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/users/", include("users.urls")),
    # Handles Google login/token exchange
    path('api/auth/social/google/', GoogleLogin.as_view(), name='google_login'),  
    
]
