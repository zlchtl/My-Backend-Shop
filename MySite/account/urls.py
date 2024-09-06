from django.urls import path
from . import views

urlpatterns = [
    path('api-register/', views.RegisterView.as_view(), name='api-register')
]