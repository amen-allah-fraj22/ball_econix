from django.urls import path
from .views import CountryComparisonAPIView

app_name = 'countries_api' # Namespace for URLs

urlpatterns = [
    path('api/compare/', CountryComparisonAPIView.as_view(), name='country_comparison_api'),
]