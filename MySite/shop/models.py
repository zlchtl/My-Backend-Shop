from django.db import models
from account.models import CustomUser


class Product(models.Model):
    """Model representing a product."""

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    rating = models.DecimalField(default=0, max_digits=2, decimal_places=1)

    def __str__(self):
        return self.name


class Cart(models.Model):
    """Model representing a user's shopping cart."""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name='wishlists')


class Comment(models.Model):
    """Model representing a comment on a product."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user} on {self.product}'