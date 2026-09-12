import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create or update the deployment administrator from environment variables.'

    def handle(self, *args, **options):
        username = os.environ.get('ADMIN_USERNAME')
        password = os.environ.get('ADMIN_PASSWORD')

        if not username or not password:
            self.stdout.write('Admin credentials not configured; skipping admin sync.')
            return

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(username=username)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(update_fields=['password', 'is_staff', 'is_superuser', 'is_active'])

        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'{action} deployment administrator: {username}'))
