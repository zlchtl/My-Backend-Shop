from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate
import re


class RegisterCustomUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def validate_password1(self, value):
        if len(value)<8:
            raise serializers.ValidationError("Пароль слишком короткий")
        return value

    def validate_username(self, value):
        if len(value)<4:
            raise serializers.ValidationError("Username слишком короткий")
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9]+$', value):
            raise serializers.ValidationError("Нельзя использовать специальные символы")
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError('Пользователь с таким username уже существует')
        return value

    def validate_email(self, value):
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9@._]+$', value):
            raise serializers.ValidationError("Нельзя использовать специальные символы")
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует')
        return value

    def validate(self, attrs):
        if attrs.get('password1') != attrs.get('password2'):
            raise serializers.ValidationError({"password2": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser(username = validated_data['username'], email = validated_data['email'])
        user.set_password(validated_data['password1'])
        user.save()
        return user

class LoginCustomUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(write_only=True, required=True, allow_blank=False)

    def validate_password(self, value):
        if len(value)<8:
            raise serializers.ValidationError("Пароль слишком короткий")
        return value

    def validate_username(self, value):
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9]+$', value):
            raise serializers.ValidationError("Нельзя использовать специальные символы")
        return value

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if user is None:
            raise serializers.ValidationError("Неверный логин или пароль.")
        attrs['user'] = user
        return attrs

