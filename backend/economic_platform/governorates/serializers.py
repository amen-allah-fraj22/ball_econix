from rest_framework import serializers
from .models import Governorate, LaborMarketData, RealEstateData, Sector, RecommendationDetails

class LaborMarketDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaborMarketData
        fields = '__all__'

class RealEstateDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealEstateData
        fields = '__all__'

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = '__all__'

class RecommendationDetailsSerializer(serializers.ModelSerializer):
    sector_name = serializers.CharField(source='sector.name', read_only=True)
    governorate_name = serializers.CharField(source='governorate.name', read_only=True)

    class Meta:
        model = RecommendationDetails
        fields = '__all__'

class GovernorateSerializer(serializers.ModelSerializer):
    labor_data = LaborMarketDataSerializer(many=True, read_only=True)
    real_estate_data = RealEstateDataSerializer(many=True, read_only=True)
    recommendations = RecommendationDetailsSerializer(many=True, read_only=True)

    class Meta:
        model = Governorate
        fields = [
            'id', 'name', 'arabic_name', 'latitude', 'longitude', 
            'population_2024', 'area_km2', 'unemployment_rate', 
            'agricultural_land_percent', 'population_density', 
            'labor_force_size', 'gdp_contribution', 'coastal_access', 
            'industrial_zones', 'tourist_attractions',
            'labor_data', 'real_estate_data', 'recommendations'
        ] 