from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import InvestmentScore
from .serializers import InvestmentOpportunitySerializer

class InvestmentAdvisorAPIView(APIView):
    def get(self, request, *args, **kwargs):
        sector = request.query_params.get('sector')
        min_investment_score_str = request.query_params.get('min_investment_score')

        if not sector:
            return Response(
                {'error': 'Sector parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = InvestmentScore.objects.filter(sector__iexact=sector)

        if min_investment_score_str:
            try:
                min_investment_score = float(min_investment_score_str)
                queryset = queryset.filter(overall_score__gte=min_investment_score)
            except ValueError:
                return Response(
                    {'error': 'Invalid min_investment_score. Must be a number.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        queryset = queryset.order_by('-overall_score')
        serializer = InvestmentOpportunitySerializer(queryset, many=True)
        return Response(serializer.data)
