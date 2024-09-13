from django.urls import path
from . import views


urlpatterns = [
    path('products/', views.ProductListCreateView.as_view(), name='product-list-create'),
    path('product/<str:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('comments/<str:slug>/', views.ProductCommentsView.as_view(), name='product-comments'),
    path('cart/', views.CartView.as_view(), name='cart-view'),
]