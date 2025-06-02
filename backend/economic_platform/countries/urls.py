from django.urls import path
from . import views # Import views to access all views in the module

app_name = 'countries_api' # Namespace for URLs

urlpatterns = [
    path('compare/', views.CountryComparisonAPIView.as_view(), name='country_comparison_api'),
    path('list-all/', views.list_all_countries_api, name='list_all_countries_api'),
]