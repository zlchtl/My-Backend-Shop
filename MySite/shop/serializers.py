from rest_framework import serializers

from .models import Product, Comment, Cart


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for the Product model."""

    author = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['slug', 'name', 'price', 'description', 'author', 'rating']
        read_only_fields = ['slug', 'author', 'rating']

    def get_author(self, obj):
        """Get the username of the product author."""
        return obj.author.username

    def validate_name(self, value):
        """Validate the product name."""
        if len(value) <= 3:
            raise serializers.ValidationError('Name must be longer than 3 characters.')
        return value

    def validate_price(self, value):
        """Validate the product price."""
        if not (0 < value < 1000000000):
            raise serializers.ValidationError('Price must be a number with a total length of up to 10 characters.')
        if len(str(value).split('.')[1]) > 2:
            raise serializers.ValidationError('The number of symbols in the fractional part must not exceed 2.')
        return value

    def validate_description(self, value):
        """Validate the product description."""
        if len(value) > 300:
            raise serializers.ValidationError("Description must not exceed 300 characters.")
        return value

    def create(self, validated_data):
        """Create a new product."""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update an existing product."""
        request_user = self.context['request'].user
        if instance.author != request_user:
            raise serializers.ValidationError("You cannot update this product.")
        return super().update(instance, validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for the Comment model."""

    author = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['product', 'rating', 'text', 'created_at', 'author']
        read_only_fields = ['product', 'author', 'created_at']

    def get_author(self, obj):
        """Get the username of the comment author."""
        return obj.author.username

    def get_product(self, obj):
        """Get the name of the product for the comment."""
        return obj.product.name

    def validate_rating(self, value):
        """Validate the rating value."""
        if value not in (1, 2, 3, 4, 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate_text(self, value):
        """Validate the comment text."""
        if len(value) > 300:
            raise serializers.ValidationError("Comment must not exceed 300 characters.")
        return value

    def create(self, validated_data):
        """Create a new comment."""
        validated_data['author'] = self.context['request'].user
        validated_data['product'] = self.context['product']
        return super().create(validated_data)


class CartSerializer(serializers.ModelSerializer):
    """Serializer for the Cart model, including product details."""

    products = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['products']

    def get_products(self, obj):
        """Retrieve the names of products in the cart."""
        return [product.name for product in obj.products.all()]


class FindProductToCartSerializer(serializers.Serializer):
    """Serializer for validating product slugs when adding to the cart."""

    product_slug = serializers.SlugField()

    def validate_product_slug(self, value):
        """Validate that the product exists based on its slug."""
        if not Product.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Product with this slug does not exist.")
        return value