import re
from rest_framework import serializers


def validate_youtube_url(value):
    """
    Валидатор для проверки ссылки, чтобы она была только на youtube.com
    """
    youtube_regex = r"^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.*$"
    if not re.match(youtube_regex, value):
        raise serializers.ValidationError("Ссылка должна быть на youtube.com.")
    return value
