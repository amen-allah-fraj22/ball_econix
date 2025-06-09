from django.urls import path
from . import views

app_name = 'frontend'  # Add namespace for URL reversing

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Country Comparison URLs
    path('compare/', views.country_comparison_select, name='country_comparison_select'),
    path('compare/results/', views.country_comparison_results, name='country_comparison_results'),
] 