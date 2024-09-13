from django.urls import path
from . import views


urlpatterns = [
    path('api-products/', views.ProductListCreateView.as_view(), name='api-product-list-create'),
    path('api-product/<str:slug>/', views.ProductDetailView.as_view(), name='api-product-detail'),
    path('api-comments/<str:slug>/', views.ProductCommentsView.as_view(), name='api-product-comments'),
    path('api-cart/', views.CartView.as_view(), name='api-cart-view'),
]