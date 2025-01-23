from django.test import TestCase
from django.contrib.auth import get_user_model
from lms.models import Course, Subscription


class CourseTestCase(TestCase):

    def setUp(self):
        # Создаём пользователя
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='password'
        )

        # Создаём курс
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Course Description',
            owner=self.user
        )

        # Создаём подписку для тестирования
        self.subscription = Subscription.objects.create(
            user=self.user,
            course=self.course
        )

    def test_subscribe_course(self):
        # Проверяем, что подписка на курс была создана
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe_course(self):
        # Удаляем подписку
        self.subscription.delete()

        # Проверяем, что подписка была удалена
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())
