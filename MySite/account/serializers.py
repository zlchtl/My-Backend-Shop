import re

from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import CustomUser, RedisKeyManager


class RegisterCustomUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def validate_password1(self, value):
        """Validate that the password is at least 8 characters long."""
        if len(value) < 8:
            raise serializers.ValidationError("Пароль слишком короткий")
        return value

    def validate_username(self, value):
        """Validate the username for length and special characters."""
        if len(value) < 4:
            raise serializers.ValidationError("Username слишком короткий")
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9]+$', value):
            raise serializers.ValidationError("Нельзя использовать специальные символы")
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError('Пользователь с таким username уже существует')
        return value

    def validate_email(self, value):
        """Validate the email for special characters and uniqueness."""
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9@._]+$', value):
            raise serializers.ValidationError("Нельзя использовать специальные символы")
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует')
        return value

    def validate(self, attrs):
        """Ensure that both passwords match."""
        if attrs.get('password1') != attrs.get('password2'):
            raise serializers.ValidationError({"password2": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        """Create a new user instance."""
        validated_data.pop('password2')
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password1'])
        user.save()
        return user


class LoginCustomUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(write_only=True, required=True, allow_blank=False)

    def validate_password(self, value):
        """Validate that the password is at least 8 characters long."""
        if len(value) < 8:
            raise serializers.ValidationError("Пароль слишком короткий")
        return value

    def validate_username(self, value):
        """Validate the username for special characters."""
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9]+$', value):
            raise serializers.ValidationError("Нельзя использовать специальные символы")
        return value

    def validate(self, attrs):
        """Authenticate the user with provided credentials."""
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if user is None:
            raise serializers.ValidationError("Неверный логин или пароль.")
        attrs['user'] = user
        return attrs

class AddAboutCustomUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name']

    def validate_name(self, value):
        """Validate name fields for special characters."""
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ]+$', value):
            raise serializers.ValidationError("Нельзя использовать специальные символы")
        return value

    def validate_first_name(self, value):
        """Validate the first name."""
        return self.validate_name(value)

    def validate_last_name(self, value):
        """Validate the last name."""
        return self.validate_name(value)


class ConfirmEmailSerializer(serializers.Serializer):
    key = serializers.CharField(required=True)

    def validate_key(self, value):
        """Validate the email confirmation key."""
        user_id = self.context['request'].user.username
        redis_key_manager = RedisKeyManager()
        redis_key = redis_key_manager.get_key(user_id=user_id, key='email')
        if value != redis_key:
            raise serializers.ValidationError("Key is not valid.")
        return value

    def save(self):
        """Confirm the user's email and clean up the redis key."""
        user_id = self.context['request'].user.username
        user = CustomUser.objects.filter(username=user_id).first()
        if not user:
            raise serializers.ValidationError("User not found.")
        user.is_email_verified = True
        user.save()

        RedisKeyManager().delete_key(user_id=user_id, key='email')
        return user

class ChangingPasswordSerializer(serializers.ModelSerializer):
    """Password serializer with saving to user"""
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['password1', 'password2']

    def validate_password1(self, value):
        """Validate that the password is at least 8 characters long."""
        if len(value) < 8:
            raise serializers.ValidationError("Пароль слишком короткий")
        return value

    def validate(self, attrs):
        """Ensure that both passwords match."""
        if attrs.get('password1') != attrs.get('password2'):
            raise serializers.ValidationError({"password2": "Пароли не совпадают."})
        return attrs

    def save(self):
        """Saving user with new password."""
        user_id = self.context['request'].user.username
        user = CustomUser.objects.filter(username=user_id).first()
        if not user:
            raise serializers.ValidationError("User not found.")
        password1 = self.validated_data['password1']
        user.set_password(password1)
        user.save()
