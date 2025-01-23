from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=255)
    preview = models.ImageField(upload_to='course_previews/', blank=True, null=True)
    description = models.TextField()
    owner = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='owned_courses')  # Строковое представление

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    preview = models.ImageField(upload_to='lesson_previews/', blank=True, null=True)
    video_url = models.URLField()
    owner = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='owned_lessons')  # Строковое представление

    def __str__(self):
        return self.title


class Subscription(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='subscriptions')  # Строковое представление
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='subscribers')

    def __str__(self):
        return f'{self.user} subscribed to {self.course}'

    class Meta:
        unique_together = ('user', 'course')
