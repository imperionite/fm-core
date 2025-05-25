from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from decouple import config

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed initial users: 1 superuser, 1 staff user, 10 regular users if no users exist'

    def create_user_with_email(self, *, username, email, password, is_staff=False, is_superuser=False, is_active=True):
        """
        Helper method to create a user and associated verified primary EmailAddress.
        """
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=is_active,
        )
        EmailAddress.objects.create(
            user=user,
            email=user.email,
            verified=False,
            primary=True,
        )
        return user

    def handle(self, *args, **options):
        # Abort if users already exist
        if User.objects.exists():
            self.stdout.write(self.style.WARNING('Users already exist. Aborting.'))
            return

        # Create superuser with verified email
        super_user = self.create_user_with_email(
            username=config('SU_USERNAME'),
            email=config('SU_EMAIL'),
            password=config('SU_PASSWORD'),
            is_staff=True,
            is_superuser=True
        )
        self.stdout.write(self.style.SUCCESS('Superuser created and email verified.'))

        # Create staff user (not superuser) with verified email
        staff_user = self.create_user_with_email(
            username=config('STAFF_USERNAME'),
            email=config('STAFF_EMAIL'),
            password=config('SU_PASSWORD'),
            is_staff=True,
            is_superuser=False
        )
        self.stdout.write(self.style.SUCCESS('Staff user created and email verified.'))

        # Create 10 regular non-staff users with verified emails
        common_password = 'passworD!123'
        for i in range(1, 11):
            self.create_user_with_email(
                username=f'user{i}',
                email=f'user{i}@grr.la',
                password=common_password,
                is_staff=False,
                is_superuser=False
            )

        self.stdout.write(self.style.SUCCESS('10 regular users created and email verified.'))