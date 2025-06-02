from django.urls import path
from .views import InvestmentAdvisorAPIView

urlpatterns = [
    path('api/investment-advisor/', InvestmentAdvisorAPIView.as_view(), name='investment_advisor_api'),
]
