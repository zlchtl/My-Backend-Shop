from django.contrib.auth import login
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import CustomUserSerializer
from rest_framework.authtoken.models import Token

# Create your views here.

#---------------API----------------
class RegisterView(APIView):
    """
    View для регистрации новых пользователей.
    """
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            user = serializer.save()
            token= Token.objects.create(user=user)
            return Response({
                'user': serializer.data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
