from django.urls import path
from . import views


urlpatterns = [
    path('products/', views.ProductListCreateView.as_view(), name='product-list-create'),
    path('product/<str:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('comments/<str:slug>/', views.ProductComments.as_view(), name='product-comments')
]