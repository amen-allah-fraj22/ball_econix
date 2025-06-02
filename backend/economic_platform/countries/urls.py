from django.urls import path
from .views import CountryComparisonAPIView, AllCountriesAPIView

app_name = 'countries_api' # Namespace for URLs

urlpatterns = [
    path('api/compare/', CountryComparisonAPIView.as_view(), name='country_comparison_api'),
    path('list-all/', AllCountriesAPIView.as_view(), name='all_countries_list_api'),
]
