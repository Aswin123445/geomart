from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from accounts.models import UserData
import os


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        self.stdout.write("===== SETUP STARTED =====")

        try:
            # Admin User
            if not UserData.objects.filter(email="admin@gmail.com").exists():
                UserData.objects.create_superuser(
                    email="admin@gmail.com",
                    name="admin",
                    phone_number="9999999999",
                    password=os.getenv("ADMIN_PASSWORD"),
                )
                self.stdout.write("Admin user created")
            else:
                self.stdout.write("Admin user already exists")

            # Site
            site, created = Site.objects.get_or_create(
                id=1,
                defaults={
                    "domain": "geomart.onrender.com",
                    "name": "GeoMart",
                },
            )

            site.domain = "geomart.onrender.com"
            site.name = "GeoMart"
            site.save()

            self.stdout.write(f"Site configured: {site.domain}")

            # Debug env vars
            self.stdout.write(
                f"GOOGLE_CLIENT_ID present: {bool(os.getenv('GOOGLE_CLIENT_ID'))}"
            )
            self.stdout.write(
                f"GOOGLE_CLIENT_SECRET present: {bool(os.getenv('GOOGLE_CLIENT_SECRET'))}"
            )

            # SocialApp
            app, created = SocialApp.objects.get_or_create(
                provider="google",
                defaults={
                    "name": "Google OAuth",
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                },
            )

            if not created:
                app.client_id = os.getenv("GOOGLE_CLIENT_ID")
                app.secret = os.getenv("GOOGLE_CLIENT_SECRET")
                app.save()

            app.sites.add(site)

            self.stdout.write(f"SocialApp configured (created={created})")

            self.stdout.write(f"SocialApp count: {SocialApp.objects.count()}")

            self.stdout.write(self.style.SUCCESS("===== INITIAL DATA CONFIGURED ====="))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"SETUP FAILED: {str(e)}"))
            raise
