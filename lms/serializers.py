from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ['owner']


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['owner']

    def get_lessons_count(self, obj):
        return obj.lessons.count()
