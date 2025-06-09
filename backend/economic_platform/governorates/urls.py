from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GovernorateViewSet, LaborMarketDataViewSet, RealEstateDataViewSet, SectorViewSet, RecommendationDetailsViewSet, InvestmentRecommendationViewSet, investment_advisor_view

router = DefaultRouter()
router.register(r'governorates', GovernorateViewSet)
router.register(r'labor-data', LaborMarketDataViewSet)
router.register(r'real-estate', RealEstateDataViewSet)
router.register(r'sectors', SectorViewSet)
router.register(r'recommendations', RecommendationDetailsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('investment-recommendations/by-sector/', InvestmentRecommendationViewSet.as_view({'get': 'by_sector'}), name='investment-by-sector'),
    path('investment-advisor/', investment_advisor_view, name='investment_advisor'),
] 