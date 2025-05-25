from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, EmailField, BooleanField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import validate_email

class User(AbstractUser):
    validate_username = UnicodeUsernameValidator()

    username = CharField(_('username'), max_length=150, blank=False,
                         unique=True, validators=[validate_username])
    email = EmailField(_('email address'), unique=True,
                       blank=False, validators=[validate_email])

    USERNAME_FIELD = 'username'
    
    EMAIL_FIELD = 'email'

    REQUIRED_FIELDS = ['email']


    def __str__(self):
        return self.username