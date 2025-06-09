from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Sum
from .models import Governorate, LaborMarketData, RealEstateData, Sector, RecommendationDetails
from .serializers import GovernorateSerializer, LaborMarketDataSerializer, RealEstateDataSerializer, SectorSerializer, RecommendationDetailsSerializer

# Create your views here.

def investment_advisor_view(request):
    return render(request, 'governorates/investment_advisor.html', {})

class GovernorateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Governorate.objects.all()
    serializer_class = GovernorateSerializer

class LaborMarketDataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LaborMarketData.objects.all()
    serializer_class = LaborMarketDataSerializer

class RealEstateDataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RealEstateData.objects.all()
    serializer_class = RealEstateDataSerializer

class SectorViewSet(viewsets.ModelViewSet):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer

class RecommendationDetailsViewSet(viewsets.ModelViewSet):
    queryset = RecommendationDetails.objects.all()
    serializer_class = RecommendationDetailsSerializer

class InvestmentRecommendationViewSet(viewsets.ViewSet):
    """ 
    A ViewSet for providing investment recommendations based on sector.
    """
    @action(detail=False, methods=['get'], url_path='by-sector')
    def by_sector(self, request):
        sector_name = request.query_params.get('sector', None)
        if not sector_name:
            return Response({'error': 'Please provide a sector name.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sector = Sector.objects.get(name__iexact=sector_name)
        except Sector.DoesNotExist:
            return Response({'error': f'Sector "{sector_name}" not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Filter recommendations by sector
        recommendations = RecommendationDetails.objects.filter(sector=sector).select_related('governorate')

        if not recommendations.exists():
            return Response({'message': f'No recommendations found for sector "{sector_name}".'}, status=status.HTTP_200_OK)

        # Prepare data for recommendations
        results = []
        for rec in recommendations:
            governorate = rec.governorate
            labor_data = LaborMarketData.objects.filter(governorate=governorate).order_by('-year').first()
            real_estate_data = RealEstateData.objects.filter(governorate=governorate).order_by('-year').first()

            results.append({
                'governorate': GovernorateSerializer(governorate).data,
                'recommendation_details': RecommendationDetailsSerializer(rec).data,
                'labor_market_data': LaborMarketDataSerializer(labor_data).data if labor_data else None,
                'real_estate_data': RealEstateDataSerializer(real_estate_data).data if real_estate_data else None,
                'ranking_score': rec.ranking_score, # Directly from RecommendationDetails
                'contact_info_investment_offices': rec.contact_info_investment_offices,
                'relevant_government_agencies': rec.relevant_government_agencies,
                'required_permits_procedures': rec.required_permits_procedures,
                'timeline_for_setup': rec.timeline_for_setup,
                'investment_size_recommendations': rec.investment_size_recommendations,
                'infrastructure_details': rec.infrastructure_details,
                'economic_incentives': rec.economic_incentives,
                'geographic_advantages': rec.geographic_advantages,
                'cost_analysis_summary': rec.cost_analysis_summary,
                'success_stories': rec.success_stories,
            })

        # You might want to add some logic here to sort/filter/rank the results
        # For example, sort by ranking_score descending
        results = sorted(results, key=lambda x: x.get('ranking_score', 0) or 0, reverse=True)

        return Response(results, status=status.HTTP_200_OK)
