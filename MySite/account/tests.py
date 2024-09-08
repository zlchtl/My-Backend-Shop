from unittest.mock import Mock, patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from .models import CustomUser, RedisKeyManager
from .serializers import (
    RegisterCustomUserSerializer,
    LoginCustomUserSerializer,
    AddAboutCustomUserSerializer,
    ConfirmEmailSerializer
)
from .services import recreate_token_service, delete_token_service


class RegisterViewTests(APITestCase):

    def setUp(self):
        """Set up the test case with initial data."""
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
        """Test successful user registration."""
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('token', response.data)
        self.assertTrue(CustomUser.objects.filter(username='testuser').exists())

    def test_register_user_with_existing_username(self):
        """Test registration with an existing username."""
        CustomUser.objects.create_user(username='testuser', email='existing@example.com', password='password')
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_register_user_with_existing_email(self):
        """Test registration with an existing email."""
        CustomUser.objects.create_user(username='existing_user', email='testuser@example.com', password='password')
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_user_invalid_email(self):
        """Test registration with an invalid email."""
        response = self.client.post(self.url, self.invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_user_weak_password(self):
        """Test registration with a weak password."""
        response = self.client.post(self.url, self.invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password1', response.data)


class RegisterCustomUserSerializerTests(TestCase):

    def test_valid_data(self):
        """Test serializer with valid data."""
        data = {
            'username': 'validuser',
            'email': 'user@example.com',
            'password1': 'strongpassword',
            'password2': 'strongpassword',
        }
        serializer = RegisterCustomUserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['username'], data['username'])

    def test_username_too_short(self):
        """Test serializer with a username that is too short."""
        data = {
            'username': 'usr',
            'email': 'user@example.com',
            'password1': 'strongpassword',
            'password2': 'strongpassword',
        }
        serializer = RegisterCustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

    def test_passwords_do_not_match(self):
        """Test serializer with mismatched passwords."""
        data = {
            'username': 'validuser',
            'email': 'user@example.com',
            'password1': 'strongpassword',
            'password2': 'differentpassword',
        }
        serializer = RegisterCustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password2', serializer.errors)

    def test_email_already_exists(self):
        """Test serializer with an existing email."""
        CustomUser.objects.create_user(username='existinguser', email='user@example.com', password='strongpassword')
        data = {
            'username': 'newuser',
            'email': 'user@example.com',
            'password1': 'strongpassword',
            'password2': 'strongpassword',
        }
        serializer = RegisterCustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_username_already_exists(self):
        """Test serializer with an existing username."""
        CustomUser.objects.create_user(username='existinguser', email='anotheruser@example.com', password='strongpassword')
        data = {
            'username': 'existinguser',
            'email': 'newuser@example.com',
            'password1': 'strongpassword',
            'password2': 'strongpassword',
        }
        serializer = RegisterCustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

    def test_create_user(self):
        """Test user creation via serializer."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'strongpassword',
            'password2': 'strongpassword',
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
        """Set up the test case with initial data for login tests."""
        self.user = CustomUser.objects.create_user(
            username='validuser',
            password='strongpassword',
            email='user@example.com'
        )

    def test_valid_data(self):
        """Test serializer with valid login data."""
        data = {
            'username': 'validuser',
            'password': 'strongpassword',
        }
        serializer = LoginCustomUserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user'], self.user)

    def test_invalid_username(self):
        """Test serializer with an invalid username format."""
        data = {
            'username': 'invalid@user!',
            'password': 'strongpassword',
        }
        serializer = LoginCustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

    def test_short_password(self):
        """Test serializer with a short password."""
        data = {
            'username': 'validuser',
            'password': 'short',
        }
        serializer = LoginCustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
        self.assertEqual(serializer.errors['password'], ["Пароль слишком короткий"])

    def test_wrong_username(self):
        """Test serializer with an incorrect username."""
        data = {
            'username': 'wronguser',
            'password': 'strongpassword',
        }
        serializer = LoginCustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_wrong_password(self):
        """Test serializer with an incorrect password."""
        data = {
            'username': 'validuser',
            'password': 'wrongpassword',
        }
        serializer = LoginCustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)


class AddAboutCustomUserSerializerTests(TestCase):

    def setUp(self):
        """Initialize user for tests involving user attributes."""
        self.user = CustomUser.objects.create_user(
            username='user',
            password='password',
            email='user@example.com'
        )

    def test_valid_data(self):
        """Test serializer with valid additional user data."""
        data = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }
        serializer = AddAboutCustomUserSerializer(instance=self.user, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Имя')
        self.assertEqual(self.user.last_name, 'Фамилия')

    def test_invalid_first_name_special_characters(self):
        """Test serializer with special characters in first name."""
        data = {
            'first_name': 'Имя!',
            'last_name': 'Фамилия',
        }
        serializer = AddAboutCustomUserSerializer(instance=self.user, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('first_name', serializer.errors)

    def test_invalid_last_name_special_characters(self):
        """Test serializer with special characters in last name."""
        data = {
            'first_name': 'Имя',
            'last_name': 'Фамилия@',
        }
        serializer = AddAboutCustomUserSerializer(instance=self.user, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('last_name', serializer.errors)

    def test_blank_first_name(self):
        """Test serializer with a blank first name."""
        data = {
            'first_name': '',
            'last_name': 'Фамилия',
        }
        serializer = AddAboutCustomUserSerializer(instance=self.user, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('first_name', serializer.errors)

    def test_blank_last_name(self):
        """Test serializer with a blank last name."""
        data = {
            'first_name': 'Имя',
            'last_name': '',
        }
        serializer = AddAboutCustomUserSerializer(instance=self.user, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('last_name', serializer.errors)


class UpdateUserViewTests(APITestCase):

    def setUp(self):
        """Set up the test case for user update tests."""
        self.url = reverse('api-update')
        self.user = CustomUser.objects.create_user(
            username='user',
            password='password',
            email='user@example.com'
        )
        _, self.token = recreate_token_service(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_update_user_success(self):
        """Test successful user update."""
        data = {
            'first_name': 'НовоеИмя',
            'last_name': 'НоваяФамилия',
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'НовоеИмя')
        self.assertEqual(self.user.last_name, 'НоваяФамилия')

    def test_update_user_invalid_data(self):
        """Test update with invalid data."""
        data = {
            'first_name': 'Имя!',
            'last_name': 'Фамилия',
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_unauthenticated(self):
        """Test unauthorized user update."""
        self.client.credentials()
        self.client.logout()
        data = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RecreateTokenViewTests(APITestCase):

    def setUp(self):
        """Set up the test case for token recreation tests."""
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        _, self.token = recreate_token_service(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.url = reverse('api-recreate-token')

    def test_recreate_token_success(self):
        """Test successful token recreation."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data['token'], self.token)

    def test_recreate_token_unauthenticated(self):
        """Test unauthorized token recreation."""
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_recreate_token_no_token(self):
        """Test token recreation when no token exists."""
        delete_token_service(self.user)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsNone(response.data.get('token'))


class ConfirmEmailSerializerTests(TestCase):

    def setUp(self):
        """Initialize test case for email confirmation serializer."""
        self.valid_data = {'key': 'valid_key'}
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        RedisKeyManager().save_key(user_id=self.user.username, key='email', value='valid_key')
        self.mock_request = Mock()
        self.mock_request.user.username = 'testuser'

    def test_valid_data(self):
        """Test serializer with valid data."""
        serializer = ConfirmEmailSerializer(data=self.valid_data, context={'request': self.mock_request})
        self.assertTrue(serializer.is_valid())

    def test_invalid_key(self):
        """Test serializer with an invalid key."""
        invalid_data = {'key': 'invalid_key'}
        serializer = ConfirmEmailSerializer(data=invalid_data, context={'request': self.mock_request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('key', serializer.errors)

    def test_missing_key(self):
        """Test serializer without a key."""
        serializer = ConfirmEmailSerializer(data={}, context={'request': self.mock_request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('key', serializer.errors)


class ConfirmEmailTests(APITestCase):

    def setUp(self):
        """Initialize test case for confirming email."""
        self.username = 'testuser'
        self.user = CustomUser.objects.create_user(username=self.username, password='testpassword')
        _, self.token = recreate_token_service(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.url = reverse('api-confirm-email')
        self.redis_manager = RedisKeyManager()

    @patch('account.services.send_async_email_service.delay')
    def test_get_request_sends_email(self, mock_send_email):
        """Test GET request triggers email sending."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_email.assert_called_once_with(self.username, self.user.email)

    def test_post_request_with_valid_key(self):
        """Test POST request with a valid key returns confirmation."""
        key = 'valid_key'
        self.redis_manager.save_key(user_id=self.username, key='email', value=key)

        response = self.client.post(self.url + f'?key={key}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'email': 'confirmed'})

        user = CustomUser.objects.get(username=self.username)
        self.assertTrue(user.is_email_verified)
        self.assertIsNone(self.redis_manager.get_key(user_id=self.username, key='email'))

    def test_post_request_with_invalid_key(self):
        """Test POST request with an invalid key returns error."""
        response = self.client.post(self.url + f'?key=invalid_key')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'key': ['Key is not valid.']})

    def test_post_request_without_key(self):
        """Test POST request without a key returns error."""
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
