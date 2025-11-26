from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        USER = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        PASS = os.environ.get("DJANGO_SUPERUSER_PASSWORD")  # HASH
        EMAIL = os.environ.get("DJANGO_SUPERUSER_EMAIL")

        if not USER or not PASS:
            print("Faltan variables.")
            return

        if User.objects.filter(username=USER).exists():
            print("El superusuario ya existe.")
            return

        user = User.objects.create(
            username=USER,
            email=EMAIL,
            is_superuser=True,
            is_staff=True,
            is_active=True,
        )
        user.password = PASS
        user.save()

        print("Superusuario creado correctamente.")