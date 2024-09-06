from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import CustomUser
from rest_framework.authtoken.models import Token

class RegisterViewTests(APITestCase):

    def setUp(self):
        self.url = reverse('api-register')
        self.valid_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'strong_password_123',
            'password2': 'strong_password_123',
        }
        self.invalid_data = {
            'username': 'testuser',
            'email': 'invalid_email',
            'password1': '123',
            'password2': '1234',
        }

    def test_register_user_success(self):
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('token', response.data)
        self.assertTrue(CustomUser.objects.filter(username='testuser').exists())

    def test_register_user_with_existing_username(self):
        # Сначала создаём пользователя
        CustomUser.objects.create_user(username='testuser', email='existing@example.com', password='password')
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_register_user_with_existing_email(self):
        # Сначала создаём пользователя
        CustomUser.objects.create_user(username='existing_user', email='testuser@example.com', password='password')
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_user_invalid_email(self):
        response = self.client.post(self.url, self.invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_user_weak_password(self):
        response = self.client.post(self.url, self.invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password1', response.data)
