from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from accounts.models import User
import os


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        # Create admin
        if not User.objects.filter(email="admin@gmail.com").exists():
            User.objects.create_superuser(
                email="admin@gmail.com",
                name="admin",
                phone_number="9999999999",
                password=os.getenv("ADMIN_PASSWORD"),
            )

        # Create site
        site, _ = Site.objects.get_or_create(
            id=1,
            defaults={
                "domain": "geomart.onrender.com",
                "name": "GeoMart",
            },
        )

        # Create Google SocialApp
        app, _ = SocialApp.objects.get_or_create(
            provider="google",
            defaults={
                "name": "Google OAuth",
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            },
        )

        app.sites.add(site)

        self.stdout.write(self.style.SUCCESS("Initial data configured"))
