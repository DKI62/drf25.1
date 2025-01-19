from django.core.management.base import BaseCommand
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Создать тестовых пользователей'

    def handle(self, *args, **kwargs):
        if not CustomUser.objects.filter(email='testuser@example.com').exists():
            CustomUser.objects.create_user(
                email='testuser@example.com',
                password='testpassword',
                phone='+1234567890',
                city='New York'
            )
            self.stdout.write('Тестовый пользователь создан.')

        if not CustomUser.objects.filter(email='admin@example.com').exists():
            CustomUser.objects.create_superuser(
                email='admin@example.com',
                password='admin'
            )
            self.stdout.write('Суперпользователь создан.')
