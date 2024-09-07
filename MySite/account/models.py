from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date
import redis
import json
from django.conf import settings

# Create your models here.
class CustomUser(AbstractUser):

    is_email_verified = models.BooleanField(default=False)
    birth_date = models.DateField(default=date.today)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


#-----------------Redis-Models-------------------
r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

class RedisKeyManager:

    def save_key(self, user_id, key, value):
        r.setex(f'user:{user_id}:key:{key}', 86400, json.dumps(value))

    def get_key(self, user_id, key):
        data = r.get(f'user:{user_id}:key:{key}')
        if data:
            return json.loads(data)
        return None

    def delete_key(self, user_id, key):
        r.delete(f'user:{user_id}:key:{key}')

    def all_key(self):
        return r.keys('*')