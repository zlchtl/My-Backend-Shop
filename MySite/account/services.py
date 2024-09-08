import uuid

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from knox.models import AuthToken
from .models import RedisKeyManager


@shared_task
def send_async_email_service(username, recipient):
    """Send a confirmation email asynchronously."""
    key = str(uuid.uuid4())
    message = (
        f'MySite \nДля подтверждения почты перейдите по ссылке\n'
        f'http://127.0.0.1:8000{reverse("api-confirm-email")}?key={key}'
    )

    your_mail = settings.EMAIL_HOST_USER

    RedisKeyManager().save_key(user_id=username, key='email', value=key)

    try:
        send_mail('MySite подтверждение почты', message, your_mail, [recipient])
    except Exception as error:
        print(f"Error sending email: {str(error)}")


def recreate_token_service(user):
    """Recreate the authentication token for the given user."""
    AuthToken.objects.filter(user=user).delete()
    return AuthToken.objects.create(user=user)


def delete_token_service(user):
    """Delete the authentication token for the given user."""
    AuthToken.objects.filter(user=user).delete()