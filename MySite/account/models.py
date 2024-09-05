from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date

# Create your models here.
class CustomUser(AbstractUser):

    is_email_verified = models.BooleanField(default=False)
    birth_date = models.DateField(default=date.today)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username