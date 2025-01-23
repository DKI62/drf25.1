from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import validate_youtube_url


class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(validators=[validate_youtube_url])

    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ['owner']


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['owner']

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user  # Получаем текущего пользователя
        return Subscription.objects.filter(user=user, course=obj).exists()  # Проверяем, есть ли подписка


class SubscriptionSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Subscription
        fields = ['user', 'course', 'course_title']
