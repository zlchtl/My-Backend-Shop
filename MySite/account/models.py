import json
from datetime import date

import redis
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model with additional fields."""

    is_email_verified = models.BooleanField(default=False)
    birth_date = models.DateField(default=date.today)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


class RedisKeyManager:
    """Manager for handling Redis keys."""

    def __init__(self):
        self.redis_instance = redis.StrictRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0
        )

    def save_key(self, user_id, key, value):
        """Save a key-value pair to Redis with an expiration time."""
        self.redis_instance.setex(f'user:{user_id}:key:{key}', 86400, json.dumps(value))

    def get_key(self, user_id, key):
        """Retrieve a value from Redis by user ID and key."""
        data = self.redis_instance.get(f'user:{user_id}:key:{key}')
        if data:
            return json.loads(data)
        return None

    def delete_key(self, user_id, key):
        """Delete a key from Redis."""
        self.redis_instance.delete(f'user:{user_id}:key:{key}')

    def all_keys(self):
        """Retrieve all keys from Redis."""
        return self.redis_instance.keys('*')