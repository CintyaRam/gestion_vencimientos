from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        print("=== Ejecutando createsu ===")

        USER = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        PASS = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        EMAIL = os.environ.get("DJANGO_SUPERUSER_EMAIL")

        print("USER:", USER)
        print("EMAIL:", EMAIL)
        print("PASS OK:", PASS is not None)

        if not User.objects.filter(username=USER).exists():
            User.objects.create_superuser(USER, EMAIL, PASS)
            print(">>> Superusuario creado con éxito.")
        else:
            print(">>> El superusuario ya existe.")