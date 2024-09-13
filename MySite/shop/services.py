from .models import Product, Comment, Cart
from .serializers import ProductSerializer, CommentSerializer, CartSerializer, FindProductToCartSerializer

def update_product_rating(product):
    """Update the rating of the given product based on its comments."""

    comments = product.comments.all()
    count = len(comments)

    if count == 0:
        return
    total_rating = sum(comment.rating for comment in comments)
    product.rating = total_rating / count


def get_cart(request):
    """Retrieve the user's cart, creating it if it does not exist."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return CartSerializer(cart).data


def add_to_cart(request, serializer):
    """Add a product to the user's cart."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product_slug = serializer.validated_data['product_slug']
    product = Product.objects.get(slug=product_slug)
    cart.products.add(product)
    return CartSerializer(cart).data


def remove_from_cart(request, serializer):
    """Remove a product from the user's cart, if it exists."""
    product_slug = serializer.validated_data['product_slug']
    product = Product.objects.get(slug=product_slug)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    if cart.products.filter(id=product.id).exists():
        cart.products.remove(product)

    return CartSerializer(cart).data


