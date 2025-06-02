from rest_framework import serializers
from .models import Country, EconomicIndicator

class CountryEconomicIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EconomicIndicator
        fields = [
            'year',
            'happiness_score',
            'gdp_per_capita',
            'headline_consumer_price_inflation',
            # Add other relevant fields from EconomicIndicator as needed
            'energy_consumer_price_inflation',
            'food_consumer_price_inflation',
            'official_core_consumer_price_inflation',
            'producer_price_inflation',
            'gdp_deflator_index_growth_rate',
            'social_support',
            'healthy_life_expectancy_at_birth',
            'freedom_to_make_life_choices',
            'generosity',
            'perceptions_of_corruption',
        ]
        # Optional: Could add read_only_fields if some fields shouldn't be updatable via this serializer

class CountryComparisonDataSerializer(serializers.ModelSerializer):
    latest_indicators = CountryEconomicIndicatorSerializer(read_only=True, source='latest_economic_indicator')
    # 'latest_economic_indicator' will be a property or annotated field on the Country model instance

    class Meta:
        model = Country
        fields = [
            'name',
            'code',
            'continent',
            'region', # Added region for more context
            'population', # Added population
            'latest_indicators'
        ]

    def to_representation(self, instance):
        """
        Dynamically fetch the latest economic indicator for the country instance.
        This method is called by DRF when serializing the object.
        """
        representation = super().to_representation(instance)

        # Fetch the latest economic indicator for this specific country instance
        latest_indicator_instance = EconomicIndicator.objects.filter(country=instance).order_by('-year').first()

        if latest_indicator_instance:
            representation['latest_indicators'] = CountryEconomicIndicatorSerializer(latest_indicator_instance).data
        else:
            representation['latest_indicators'] = None # Or an empty dict, or a specific message

        return representation
