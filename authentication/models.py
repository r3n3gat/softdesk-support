# authentication/models.py

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.exceptions import ValidationError

class User(AbstractUser):
    age = models.PositiveIntegerField(null=True, blank=True, default=18)
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now_add=True)

    # Utilise des related_name uniques pour éviter les collisions
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',
        blank=True,
        help_text='Groupes auxquels l’utilisateur appartient.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',
        blank=True,
        help_text='Permissions spécifiques de l’utilisateur.',
        verbose_name='user permissions'
    )

    def clean(self):
        if self.age is not None and self.age < 15:
            raise ValidationError("L'utilisateur doit avoir au moins 15 ans.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'authentication'
