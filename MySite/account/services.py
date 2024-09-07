from knox.models import AuthToken
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def SendAsyncEmailService(recipient):
    message = 'test'
    your_mail = settings.EMAIL_HOST_USER
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