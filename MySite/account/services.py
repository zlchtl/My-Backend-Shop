from knox.models import AuthToken
from celery import shared_task
from django.core.mail import send_mail
from decouple import config

@shared_task
def SendAsyncEmailService(recipient):
    message = 'test'
    EMAIL_HOST_USER = config('EMAIL_HOST_USER')
    try:
        send_mail('MySite подтверждение почты', message,
                  EMAIL_HOST_USER, [recipient])
    except Exception as e:
        print(f"Error sending email: {str(e)}")

def RecreateTokenService(user):
    AuthToken.objects.filter(user=user).delete()
    return AuthToken.objects.create(user=user)

def DeleteTokenService(user):
    AuthToken.objects.filter(user=user).delete()