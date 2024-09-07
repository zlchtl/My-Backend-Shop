from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import CustomUser
from .serializers import RegisterCustomUserSerializer, LoginCustomUserSerializer, AddAboutCustomUserSerializer
from .services import RecreateTokenService, DeleteTokenService


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
        CustomUser.objects.create_user(username='testuser', email='existing@example.com', password='password')
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_register_user_with_existing_email(self):
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


class RegisterCustomUserSerializerTests(TestCase):

    def test_valid_data(self):
        data = {
            'username': 'validuser',
            'email': 'user@example.com',
            'password1': 'strongpassword',
            'password2': 'strongpassword'
        }
        serializer = RegisterCustomUserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['username'], data['username'])

    def test_username_too_short(self):
        data = {
            'username': 'usr',
            'email': 'user@example.com',
            'password1': 'strongpassword',
            'password2': 'strongpassword'
        }
        serializer = RegisterCustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

    def test_passwords_do_not_match(self):
        data = {
            'username': 'validuser',
            'email': 'user@example.com',
            'password1': 'strongpassword',
            'password2': 'differentpassword'
        }
        serializer = RegisterCustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password2', serializer.errors)

    def test_email_already_exists(self):
        CustomUser.objects.create_user(username='existinguser', email='user@example.com', password='strongpassword')
        data = {
            'username': 'newuser',
            'email': 'user@example.com',
            'password1': 'strongpassword',
            'password2': 'strongpassword'
        }
        serializer = RegisterCustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_username_already_exists(self):
        CustomUser.objects.create_user(username='existinguser', email='anotheruser@example.com',
                                       password='strongpassword')
        data = {
            'username': 'existinguser',
            'email': 'newuser@example.com',
            'password1': 'strongpassword',
            'password2': 'strongpassword'
        }
        serializer = RegisterCustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

    def test_create_user(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'strongpassword',
            'password2': 'strongpassword'
        }
        serializer = RegisterCustomUserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertIsInstance(user, CustomUser)
        self.assertEqual(user.username, data['username'])
        self.assertEqual(user.email, data['email'])
        self.assertTrue(user.check_password(data['password1']))


class LoginCustomUserSerializerTests(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='validuser',
            password='strongpassword',
            email='user@example.com'
        )

    def test_valid_data(self):
        data = {
            'username': 'validuser',
            'password': 'strongpassword'
        }
        serializer = LoginCustomUserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user'], self.user)

    def test_invalid_username(self):
        data = {
            'username': 'invalid@user!',
            'password': 'strongpassword'
        }
        serializer = LoginCustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

    def test_short_password(self):
        data = {
            'username': 'validuser',
            'password': 'short'
        }
        serializer = LoginCustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
        self.assertEqual(serializer.errors['password'], ["Пароль слишком короткий"])

    def test_wrong_username(self):
        data = {
            'username': 'wronguser',
            'password': 'strongpassword'
        }
        serializer = LoginCustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_wrong_password(self):
        data = {
            'username': 'validuser',
            'password': 'wrongpassword'
        }
        serializer = LoginCustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)


class AddAboutCustomUserSerializerTests(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='user',
            password='password',
            email='user@example.com'
        )

    def test_valid_data(self):
        data = {
            'first_name': 'Имя',
            'last_name': 'Фамилия'
        }
        serializer = AddAboutCustomUserSerializer(instance=self.user, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Имя')
        self.assertEqual(self.user.last_name, 'Фамилия')

    def test_invalid_first_name_special_characters(self):
        data = {
            'first_name': 'Имя!',
            'last_name': 'Фамилия'
        }
        serializer = AddAboutCustomUserSerializer(instance=self.user, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('first_name', serializer.errors)

    def test_invalid_last_name_special_characters(self):
        data = {
            'first_name': 'Имя',
            'last_name': 'Фамилия@'
        }
        serializer = AddAboutCustomUserSerializer(instance=self.user, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('last_name', serializer.errors)

    def test_blank_first_name(self):
        data = {
            'first_name': '',
            'last_name': 'Фамилия'
        }
        serializer = AddAboutCustomUserSerializer(instance=self.user, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('first_name', serializer.errors)

    def test_blank_last_name(self):
        data = {
            'first_name': 'Имя',
            'last_name': ''
        }
        serializer = AddAboutCustomUserSerializer(instance=self.user, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('last_name', serializer.errors)

class UpdateUserViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('api-update')
        self.user = CustomUser.objects.create_user(
            username='user',
            password='password',
            email='user@example.com'
        )
        _, self.token = RecreateTokenService(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_update_user_success(self):
        data = {
            'first_name': 'НовоеИмя',
            'last_name': 'НоваяФамилия'
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'НовоеИмя')
        self.assertEqual(self.user.last_name, 'НоваяФамилия')

    def test_update_user_invalid_data(self):
        data = {
            'first_name': 'Имя!',
            'last_name': 'Фамилия'
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_unauthenticated(self):
        self.client.credentials()
        self.client.logout()
        data = {
            'first_name': 'Имя',
            'last_name': 'Фамилия'
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class RecreateTokenViewTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        _, self.token = RecreateTokenService(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.url = reverse('api-recreate-token')

    def test_recreate_token_success(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data['token'], self.token)

    def test_recreate_token_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_recreate_token_no_token(self):
        DeleteTokenService(self.user)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsNone(response.data.get('token'))

