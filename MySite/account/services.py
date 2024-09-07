from knox.models import AuthToken

def RecreateTokenService(user):
    AuthToken.objects.filter(user=user).delete()
    return AuthToken.objects.create(user=user)

def DeleteTokenService(user):
    AuthToken.objects.filter(user=user).delete()