from django.core.management.base import BaseCommand
from users.models import Payment
from lms.models import Course, Lesson
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Создаёт тестовые платежи"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        user1 = User.objects.first()
        course = Course.objects.first()
        lesson = Lesson.objects.first()

        Payment.objects.create(user=user1, course=course, amount=100.00, payment_method="cash")
        Payment.objects.create(user=user1, lesson=lesson, amount=50.00, payment_method="transfer")
        self.stdout.write(self.style.SUCCESS("Тестовые платежи добавлены!"))
