from django.urls import path
from . import views

urlpatterns = [
    path('api-register/', views.RegisterView.as_view(), name='api-register'),
    path('api-login/', views.LoginView.as_view(), name='api-login'),
    path('api-update/', views.UpdateUserView.as_view(), name='api-update'),
    path('api-recreate-token/', views.RecreateTokenView.as_view(), name='api-recreate-token'),
    path('api-confirm-email/', views.ConfirmEmailView.as_view(), name='api-confirm-email'),
    path('api-confirm-email/<str:key>', views.ConfirmEmailView.as_view()),
    path('api-profile/', views.ProfileView.as_view(), name='api-profile'),
    path('api-change-password/', views.ChangingPasswordView.as_view(), name='api-change-password')
]