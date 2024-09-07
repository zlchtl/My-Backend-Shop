from knox.models import AuthToken
from .models import RedisKeyManager
from celery import shared_task
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
import uuid

@shared_task
def SendAsyncEmailService(username, recipient):
    key = str(uuid.uuid4())
    message = (f'MySite \nДля подтверждения почты перейдите по ссылке\n'
               f'http://127.0.0.1:8000{reverse('api-confirm-email')}?key={key}')   #TODO заменить на что-то нормальное
    your_mail = settings.EMAIL_HOST_USER

    RedisKeyManager().save_key(user_id=username, key='email', value=key)

    try:
        send_mail('MySite подтверждение почты', message,
                  your_mail, [recipient])
    except Exception as e:
        print(f"Error sending email: {str(e)}")

def RecreateTokenService(user):
    AuthToken.objects.filter(user=user).delete()
    return AuthToken.objects.create(user=user)

def DeleteTokenService(user):
    AuthToken.objects.filter(user=user).delete()