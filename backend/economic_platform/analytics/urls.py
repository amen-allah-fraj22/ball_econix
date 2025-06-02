from django.urls import path
from . import views

app_name = 'analytics_api' # Namespace for URLs

urlpatterns = [
    path('global-dashboard-data/', views.global_dashboard_data, name='global_dashboard_data'),
    path('search-countries/', views.search_countries, name='search_countries'),
    path('country-detail/<str:country_name>/', views.country_detail_data, name='country_detail_data'),
    path('inflation-trends/', views.inflation_trends, name='inflation_trends'),
    path('correlation-analysis/', views.correlation_analysis, name='correlation_analysis'),
    path('test-chart/', views.test_chart_view, name='test_chart_view'), # New URL for the test chart
    path('real-estate-trends/<int:governorate_id>/', views.real_estate_price_trends_api, name='real_estate_price_trends_api'),
    path('labor-market-trends/<int:governorate_id>/', views.labor_market_trends_api, name='labor_market_trends_api'),
    path('tunisia-map/', views.tunisia_map_view, name='tunisia_map_view'), # URL for the Tunisia map page
    path('world-map/', views.world_map_view, name='world_map_page'), # URL for the new World Map page
]