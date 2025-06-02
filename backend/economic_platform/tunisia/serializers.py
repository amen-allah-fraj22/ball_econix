from rest_framework import serializers
from .models import TunisiaGovernorate, InvestmentScore

class GovernorateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TunisiaGovernorate
        fields = ['name', 'population_2024', 'area_km2']

class InvestmentOpportunitySerializer(serializers.ModelSerializer):
    governorate = GovernorateSerializer(read_only=True)
    class Meta:
        model = InvestmentScore
        fields = [
            'sector',
            'overall_score',
            'labor_score',
            'infrastructure_score',
            'tax_incentive_score',
            'market_access_score',
            'reasoning',
            'governorate'
        ]
