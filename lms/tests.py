from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.utils import json

from .models import Course, Lesson, Subscription
from users.models import CustomUser


class TestCase(APITestCase):
    """
    Базовый тестовый класс для всех тестов
    """

    def setUp(self):
        self.user = CustomUser.objects.create_user(email="test@test.ru", password="password")
        self.course = Course.objects.create(title="Test Course", owner=self.user, description="Test Description")
        self.lesson = Lesson.objects.create(
            title="Test Lesson", course=self.course, owner=self.user, description="Test Lesson Description", video_url="https://example.com/video"
        )
        self.client.force_authenticate(user=self.user)


class CourseTestCase(TestCase):
    """
    Тесты для работы с курсами
    """

    def test_course_retrieve(self):
        """
        Тест получения курса по ID
        """
        url = reverse("course-detail", args=[self.course.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], self.course.title)

    def test_course_create(self):
        """
        Тест создания нового курса
        """
        url = reverse("course-list")
        data = {
            "title": "New Course",
            "description": "Description of new course",
            "owner": self.user.pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Course.objects.count(), 2)

    def test_course_update(self):
        """
        Тест изменения курса по ID
        """
        url = reverse("course-detail", args=[self.course.pk])
        data = {
            "title": "Updated Test Course",
            "description": "Updated description",
        }
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Course.objects.get(pk=self.course.pk).title, "Updated Test Course")

    def test_course_delete(self):
        """
        Тест удаления курса по ID
        """
        url = reverse("course-detail", args=[self.course.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Course.objects.count(), 0)


class LessonTestCase(TestCase):
    """
    Тесты для работы с уроками
    """

    def test_lesson_retrieve(self):
        """
        Тест получения урока по ID
        """
        url = reverse("lesson-detail", args=[self.lesson.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], self.lesson.title)

    def test_lesson_create(self):
        url = reverse("lesson-list")
        data = {
            "title": "Test Lesson 2",
            "course": self.course.pk,
            "owner": self.user.pk,
            "description": "Test Lesson 2 Description",
            "video_url": "https://www.youtube.com/"
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_update(self):
        url = reverse("lesson-detail", args=[self.lesson.pk])
        data = {
            "title": "Updated Test Lesson",
            "course": self.course.pk,
            "description": "Updated lesson description",
            "preview": None,
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.put(url, data=json.dumps(data), content_type="application/json")

        print("Response Status Code:", response.status_code)
        print("Response Data:", response.json())

        self.assertEqual(response.status_code, 200)

    def test_lesson_delete(self):
        """
        Тест удаления урока по ID
        """
        url = reverse("lesson-detail", args=[self.lesson.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Lesson.objects.count(), 0)


class SubscriptionTest(TestCase):
    """
    Тесты для работы с подписками
    """

    def test_subscription_create(self):
        url = reverse("subscribe-course")
        data = {
            "course_id": self.course.pk
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Subscription added.", response.json()["message"])

    def test_subscription_delete(self):
        """
        Тест отмены подписки
        """
        subscription = Subscription.objects.create(user=self.user, course=self.course)
        url = reverse("subscription")
        response = self.client.delete(url, data={"user_id": self.user.pk, "course_id": self.course.pk})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Subscription.objects.count(), 0)
