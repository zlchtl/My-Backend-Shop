from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Product, Comment
from account.models import CustomUser
from knox.models import AuthToken


class ProductAPITests(APITestCase):
    """Tests for the Product API."""

    def setUp(self):
        """Set up test user and product."""
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')

        self.product = Product.objects.create(
            name='Test Product',
            price=100.00,
            description='This is a test product.',
            author=self.user
        )

        self.token = AuthToken.objects.create(user=self.user)[1]

    def authenticate(self):
        """Authenticate the test client using the created user."""
        self.client.force_login(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_get_products(self):
        """Test retrieval of all products."""
        self.authenticate()
        response = self.client.get(reverse('product-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_product(self):
        """Test creation of a new product."""
        self.authenticate()
        url = reverse('product-list-create')
        data = {
            'name': 'New Product',
            'price': 150.00,
            'description': 'This is a new product.'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(Product.objects.get(id=2).name, 'New Product')

    def test_get_product_detail(self):
        """Test retrieval of a product by slug."""
        self.authenticate()
        response = self.client.get(reverse('product-detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')

    def test_update_product(self):
        """Test updating a product's description."""
        self.authenticate()
        url = reverse('product-detail', kwargs={'slug': self.product.slug})
        response = self.client.patch(url, {'description': 'Updated description'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.description, 'Updated description')

    def test_update_product_not_author(self):
        """Test trying to update a product by a non-author user."""
        other_user = CustomUser.objects.create_user(username='otheruser', password='otherpassword')
        other_token = AuthToken.objects.create(user=other_user)[1]

        url = reverse('product-detail', kwargs={'slug': self.product.slug})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + other_token)
        response = self.client.patch(url, {'description': 'Hacking attempt!'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_product_comments(self):
        """Test retrieval of comments for a product."""
        self.authenticate()
        Comment.objects.create(product=self.product, text="Great product!", author=self.user, rating=5)

        response = self.client.get(reverse('product-comments', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_comment(self):
        """Test creation of a new comment for a product."""
        self.authenticate()
        url = reverse('product-comments', kwargs={'slug': self.product.slug})
        data = {
            'rating': 5,
            'text': 'This is a comment.'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)