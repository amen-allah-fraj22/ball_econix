from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import UserProfile
from tunisia.models import TunisiaGovernorate # Import TunisiaGovernorate
import json

User = get_user_model()

# Frontend Template Views
def login_view(request):
    """Render login page"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                return redirect('auth:dashboard')
            else:
                messages.error(request, 'Invalid credentials')
        except Exception:
            messages.error(request, 'User does not exist or invalid credentials')
    
    return render(request, 'auth/login.html')

def register_view(request):
    """Render registration page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Basic validation
        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
            return render(request, 'auth/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'auth/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'auth/register.html')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            # Create profile
            UserProfile.objects.create(user=user)
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('auth:login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    
    return render(request, 'auth/register.html')

@login_required
def profile_view(request):
    """User profile page"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update user info
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.phone = request.POST.get('phone', '')
        request.user.country = request.POST.get('country', '')
        request.user.profession = request.POST.get('profession', '')
        request.user.save()
        
        # Update profile info
        profile.bio = request.POST.get('bio', '')
        profile.location = request.POST.get('location', '')
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('auth:profile')
    
    return render(request, 'auth/profile.html', {'profile': profile})

@login_required
def dashboard_view(request):
    """Main dashboard"""
    governorates = TunisiaGovernorate.objects.all().values('id', 'name', 'latitude', 'longitude', 'population_2024', 'unemployment_rate')
    context = {
        'governorates_data_json': json.dumps(list(governorates))
    }
    print(f"DEBUG: governorates_data_json: {context['governorates_data_json']}") # Temporary debug print
    return render(request, 'dashboard/main.html', context)

def logout_view(request):
    """Logout user"""
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('auth:login')

# API Views for AJAX requests
@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """API endpoint for login"""
    email = request.data.get('email')
    password = request.data.get('password')
    
    try:
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return Response({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })
        else:
            return Response({
                'success': False,
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception:
        return Response({
            'success': False,
            'message': 'User does not exist or invalid credentials'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    """API endpoint for registration"""
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        password = request.data.get('password')
        
        # Check if user exists
        if User.objects.filter(email=email).exists():
            return Response({
                'success': False,
                'message': 'Email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        
        # Create profile
        UserProfile.objects.create(user=user)
        
        return Response({
            'success': True,
            'message': 'Registration successful'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)