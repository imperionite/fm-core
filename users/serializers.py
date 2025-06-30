from rest_framework import serializers
from dj_rest_auth.serializers import UserDetailsSerializer
from allauth.account.models import EmailAddress


class CustomUserDetailsSerializer(UserDetailsSerializer):
    email_verified = serializers.SerializerMethodField()

    def get_email_verified(self, obj):
        # Check if the user's email is verified using allauth's EmailAddress model
        return EmailAddress.objects.filter(
            user=obj, email=obj.email, verified=True
        ).exists()

    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + (
            "email_verified",
            "last_login",
            "date_joined",
            "is_active",
            "is_staff",
            "is_superuser",
        )
