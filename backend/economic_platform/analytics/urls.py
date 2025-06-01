from django.urls import path
from . import views

app_name = 'analytics_api' # Namespace for URLs

urlpatterns = [
    path('global-dashboard-data/', views.global_dashboard_data, name='global_dashboard_data'),
    path('search-countries/', views.search_countries, name='search_countries'),
    path('country-detail/<str:country_name>/', views.country_detail_data, name='country_detail_data'),
    path('inflation-trends/', views.inflation_trends, name='inflation_trends'),
    path('correlation-analysis/', views.correlation_analysis, name='correlation_analysis'),
]