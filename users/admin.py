from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Informations complémentaires",
            {"fields": ("phone", "address", "is_patient", "is_doctor")},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Informations complémentaires",
            {"fields": ("first_name", "last_name", "email", "phone", "address", "is_patient", "is_doctor")},
        ),
    )
    list_display = ("username", "email", "first_name", "last_name", "is_patient", "is_doctor", "is_staff")
    list_filter = ("is_patient", "is_doctor", "is_staff", "is_superuser")
