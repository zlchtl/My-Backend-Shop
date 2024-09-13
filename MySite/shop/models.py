from django.db import models
from account.models import CustomUser
from django.utils.text import slugify


class Product(models.Model):
    """Model representing a product."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    rating = models.DecimalField(default=0, max_digits=2, decimal_places=1)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Create a unique slug for the product."""
        if not self.slug:
            original_slug = slugify(self.name)
            self.slug = original_slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)


class Cart(models.Model):
    """Model representing a user's shopping cart."""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name='products')

    def __str__(self):
        return f'{self.user}`s cart'


class Comment(models.Model):
    """Model representing a comment on a product."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.product.slug}'