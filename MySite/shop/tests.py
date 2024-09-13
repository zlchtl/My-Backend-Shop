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


class CartAPITests(APITestCase):

    def setUp(self):
        """Set up the test user, products, and authentication."""
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.token = AuthToken.objects.create(user=self.user)[1]

        self.product1 = Product.objects.create(
            name='Product 1',
            price=10.00,
            description='Description 1',
            author=self.user
        )
        self.product1.slug = 'product-1'
        self.product1.save()

        self.product2 = Product.objects.create(
            name='Product 2',
            price=20.00,
            description='Description 2',
            author=self.user
        )
        self.product2.slug = 'product-2'
        self.product2.save()

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_get_cart(self):
        """Test retrieving the cart."""
        response = self.client.get(reverse('cart-view'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['products'], [])

    def test_add_product_to_cart(self):
        """Test adding a product to the cart."""
        data = {'product_slug': self.product1.slug}
        response = self.client.post(reverse('cart-view'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.product1.name, response.data['products'])

    def test_remove_product_from_cart(self):
        """Test removing a product from the cart."""
        self.client.post(reverse('cart-view'), {'product_slug': self.product1.slug})

        data = {'product_slug': self.product1.slug}
        response = self.client.delete(reverse('cart-view'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.product1.name, response.data['products'])

    def test_add_non_existent_product_to_cart(self):
        """Test adding a non-existent product to the cart."""
        data = {'product_slug': 'non-existent-slug'}
        response = self.client.post(reverse('cart-view'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('product_slug', response.data)
        self.assertEqual(response.data['product_slug'][0], "Product with this slug does not exist.")

    def test_remove_non_existent_product_from_cart(self):
        """Test removing a non-existent product from the cart."""
        data = {'product_slug': 'non-existent-slug'}
        response = self.client.delete(reverse('cart-view'), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)