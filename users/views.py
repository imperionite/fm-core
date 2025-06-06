from django.contrib.auth import get_user_model
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.throttling import AnonRateThrottle
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import LoginView


from decouple import config

from .serializers import CustomUserDetailsSerializer
from .permissions import IsOwnerOrAdmin


User = get_user_model()

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = config('CALLBACK_URL')

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = self.user
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            return Response({
                'access': access_token,
                'refresh': refresh_token
            }, status=status.HTTP_200_OK)
        else:
            return response

# Just a soft-delete or deactivation through delete 
class UserDeactivateView(generics.DestroyAPIView):
    permission_classes = [IsOwnerOrAdmin, IsAuthenticated]
    authentication_classes = [JWTAuthentication, TokenAuthentication]
    serializer_class = CustomUserDetailsSerializer
    lookup_field = 'username'
    queryset = User.objects.all()

    def perform_destroy(self, instance):
        # Instead of deleting, deactivate
        instance.is_active = False
        instance.save()

class LoginThrottleView(LoginView):
    throttle_classes = [AnonRateThrottle]

class GoogleLoginThrottleView(GoogleLogin):
    throttle_classes = [AnonRateThrottle] 
