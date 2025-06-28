from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

# from .forms import UserChangeForm, UserCreationForm

User = get_user_model()

@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    fieldsets = auth_admin.UserAdmin.fieldsets
    list_display = ['pk', 'username', 'email',
                    'is_superuser', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['email',]
 