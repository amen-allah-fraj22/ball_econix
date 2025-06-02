from django.urls import path
from . import views # Import views generally

urlpatterns = [
    path('investment-advisor/', views.InvestmentAdvisorAPIView.as_view(), name='api_investment_advisor'),
    # Add other Tunisia-specific API endpoints here if any
]
