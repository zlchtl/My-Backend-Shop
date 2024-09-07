from django.urls import path
from . import views

urlpatterns = [
    path('api-register/', views.RegisterView.as_view(), name='api-register'),
    path('api-login/', views.LoginView.as_view(), name='api-login'),
    path('api-update/', views.UpdateUserView.as_view(), name='api-update'),
    path('api-recreate-token/', views.RecreateTokenView.as_view(), name='api-recreate-token'),
]