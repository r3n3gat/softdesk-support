from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


# === Formulaires intégrés (pas de forms.py séparé) ===

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        # On inclut ici les champs personnalisés afin qu'ils soient bien sauvegardés à la création
        fields = (
            "username", "email", "age",
            "can_be_contacted", "can_data_be_shared",
        )

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            "username", "first_name", "last_name", "email", "age",
            "can_be_contacted", "can_data_be_shared",
            "is_active", "is_staff", "is_superuser", "groups", "user_permissions",
        )


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # On branche nos formulaires
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    # Liste
    list_display = (
        "username", "email", "age",
        "can_be_contacted", "can_data_be_shared",
        "is_staff", "is_active", "created_time",
    )
    list_filter = ("is_staff", "is_active", "can_be_contacted", "can_data_be_shared")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)
    list_per_page = 50
    date_hierarchy = "date_joined"

    # Readonly
    readonly_fields = ("created_time", "last_login", "date_joined")

    # UI pratique pour M2M (tu as conservé les champs 'groups' et 'user_permissions')
    filter_horizontal = ("groups", "user_permissions")

    # Organisation des formulaires
    fieldsets = (
        ("Identifiants", {"fields": ("username", "email", "password")}),
        ("Infos personnelles", {
            "fields": ("first_name", "last_name", "age", "can_be_contacted", "can_data_be_shared")
        }),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        ("Dates", {"fields": ("last_login", "date_joined", "created_time")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "email", "age",
                "can_be_contacted", "can_data_be_shared",
                "password1", "password2",
            ),
        }),
    )
