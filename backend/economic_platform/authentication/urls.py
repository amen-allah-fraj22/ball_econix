from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Template views
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    
    # API endpoints
    path('api-login/', views.api_login, name='api_login'),
    path('api-register/', views.api_register, name='api_register'),
]