from knox.models import AuthToken
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import (
    RegisterCustomUserSerializer,
    LoginCustomUserSerializer,
    AddAboutCustomUserSerializer,
    ConfirmEmailSerializer
)
from .services import recreate_token_service, send_async_email_service

#---------------API----------------
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Register a new user and return the user and token."""
        serializer = RegisterCustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = AuthToken.objects.create(user=user)
            return Response({
                'user': serializer.data,
                'token': token[1]
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Login an existing user and return the user and token."""
        serializer = LoginCustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            _, token = recreate_token_service(user)
            return Response({
                'user': serializer.data,
                'token': token,
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """Update the authenticated user's information."""
        user = request.user
        serializer = AddAboutCustomUserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'update': 'success'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RecreateTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Recreate a token for the authenticated user."""
        user = request.user
        _, token = recreate_token_service(user)
        return Response({
            'user': user.username,
            'token': token
        }, status=status.HTTP_201_CREATED)

class ConfirmEmail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Send a confirmation email to the authenticated user."""
        send_async_email_service.delay(request.user.username, request.user.email)
        return Response({'test': 'test'}, status=status.HTTP_200_OK)

    def post(self, request):
        """Confirm the user's email using the provided key."""
        key = request.GET.get('key')
        serializer = ConfirmEmailSerializer(data={'key': key}, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'email': 'confirmed'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)