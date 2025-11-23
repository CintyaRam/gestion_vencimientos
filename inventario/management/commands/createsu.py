from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        USER = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        PASS = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        EMAIL = os.environ.get("DJANGO_SUPERUSER_EMAIL")

        if not User.objects.filter(username=USER).exists():
            User.objects.create_superuser(USER, EMAIL, PASS)
            print("Superusuario creado.")
        else:
            print("Superusuario ya existe.")