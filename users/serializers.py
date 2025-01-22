from rest_framework import serializers
from .models import CustomUser, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True, source='payment_set')

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'phone', 'city', 'avatar', 'payments']
        read_only_fields = ['id', 'payments']

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value
