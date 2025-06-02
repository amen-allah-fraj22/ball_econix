from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from countries.models import Country, EconomicIndicator # Ensure these are the correct model names
from tunisia.models import RealEstatePrices, TunisiaGovernorate # Import RealEstatePrices and TunisiaGovernorate
from .models import LaborMarketData # Import LaborMarketData
from .chart_configs import CHART_CONFIGURATIONS # For potential use in correlation_analysis later
from django.db.models import Max, F, Q, Avg
from django.db.models.functions import ExtractYear
from django.shortcuts import get_object_or_404, render # Added import, and render
import pandas as pd # For potential complex data manipulation, if needed

# New view for testing Chart.js
def test_chart_view(request):
    labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
    data = [10, 22, 15, 28, 12]
    context = {
        'labels': labels,
        'data': data,
        'chart_title': 'Sample Bar Chart',
        'chart_type': 'bar'
    }
    return render(request, 'analytics/test_chart.html', context)

@api_view(['GET'])
def global_dashboard_data(request):
    try:
        latest_year_data = EconomicIndicator.objects.aggregate(latest_year=Max('year'))
        latest_year = latest_year_data.get('latest_year')

        if not latest_year:
            return Response([], status=status.HTTP_200_OK)

        countries_with_happiness = Country.objects.filter(
            economic_indicators__year=latest_year,
            economic_indicators__happiness_score__isnull=False,
            latitude__isnull=False,
            longitude__isnull=False
        ).annotate(
            latest_happiness_score=F('economic_indicators__happiness_score')
        ).values(
            'name',
            'latest_happiness_score',
            'latitude',
            'longitude',
            'code'
        ).distinct()

        formatted_data = []
        for country_data in countries_with_happiness:
            formatted_data.append({
                'country': country_data['name'],
                'happiness': country_data['latest_happiness_score'],
                'lat': country_data['latitude'],
                'lng': country_data['longitude'],
                'code': country_data['code']
            })

        return Response(formatted_data)
    except Exception as e:
        print(f"Error in global_dashboard_data: {e}")
        return Response({'error': 'An unexpected error occurred. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def search_countries(request):
    query = request.query_params.get('q', None)
    if not query:
        return Response([], status=status.HTTP_200_OK)

    try:
        latest_year_overall_data = EconomicIndicator.objects.aggregate(max_year=Max('year'))
        latest_year_overall = latest_year_overall_data.get('max_year')

        countries_qs = Country.objects.filter(
            Q(name__icontains=query) | Q(code__iexact=query)
        )

        results = []
        for country in countries_qs:
            data = {
                'name': country.name,
                'code': country.code,
                'continent': country.continent,
                'region': country.region,
                'happiness_score': None
            }
            if latest_year_overall:
                latest_indicator = EconomicIndicator.objects.filter(
                    country=country,
                    year=latest_year_overall,
                    happiness_score__isnull=False
                ).values('happiness_score').first()
                if latest_indicator:
                    data['happiness_score'] = latest_indicator['happiness_score']
            results.append(data)

        results.sort(key=lambda x: (
            x['code'].lower() != query.lower(),
            not x['name'].lower().startswith(query.lower()),
            x['name']
        ))

        return Response(results[:10])
    except Exception as e:
        print(f"Error in search_countries: {e}")
        return Response({'error': 'An unexpected error occurred. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def country_detail_data(request, country_name):
    try:
        country = get_object_or_404(Country, Q(name__iexact=country_name) | Q(code__iexact=country_name))
        indicators = EconomicIndicator.objects.filter(country=country).order_by('year')

        country_info = {
            'name': country.name,
            'code': country.code,
            'continent': country.continent,
            'region': country.region,
            'population': country.population,
            'latitude': country.latitude,
            'longitude': country.longitude,
        }

        if not indicators.exists():
            return Response({
                'country_info': country_info,
                'error': 'No economic indicator data found for this country.'
            }, status=status.HTTP_200_OK) # Changed to 200 with error message in body as per common practice

        indicator_data_list = []
        for ind in indicators:
            indicator_data_list.append({
                'year': ind.year,
                'headline_consumer_price_inflation': ind.headline_consumer_price_inflation,
                'energy_consumer_price_inflation': ind.energy_consumer_price_inflation,
                'food_consumer_price_inflation': ind.food_consumer_price_inflation,
                'official_core_consumer_price_inflation': ind.official_core_consumer_price_inflation,
                'producer_price_inflation': ind.producer_price_inflation,
                'gdp_deflator_index_growth_rate': ind.gdp_deflator_index_growth_rate,
                'happiness_score': ind.happiness_score,
                'gdp_per_capita': ind.gdp_per_capita,
                'social_support': ind.social_support,
                'healthy_life_expectancy_at_birth': ind.healthy_life_expectancy_at_birth,
                'freedom_to_make_life_choices': ind.freedom_to_make_life_choices,
                'generosity': ind.generosity,
                'perceptions_of_corruption': ind.perceptions_of_corruption,
            })

        response_data = {
            'country_info': country_info,
            'economic_indicators': indicator_data_list,
        }
        return Response(response_data)
    except Country.DoesNotExist: # This is technically handled by get_object_or_404, but kept for clarity
         return Response({'error': f"Country '{country_name}' not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error in country_detail_data for {country_name}: {e}")
        return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def inflation_trends(request):
    try:
        filters = Q()
        continent = request.query_params.get('continent', None)
        country_name_or_code = request.query_params.get('country', None)
        start_year = request.query_params.get('start_year', None)
        end_year = request.query_params.get('end_year', None)

        if continent:
            filters &= Q(country__continent__iexact=continent)
        if country_name_or_code:
            filters &= (Q(country__name__iexact=country_name_or_code) | Q(country__code__iexact=country_name_or_code))
        if start_year:
            try:
                filters &= Q(year__gte=int(start_year))
            except ValueError:
                return Response({'error': 'Invalid start_year format.'}, status=status.HTTP_400_BAD_REQUEST)
        if end_year:
            try:
                filters &= Q(year__lte=int(end_year))
            except ValueError:
                return Response({'error': 'Invalid end_year format.'}, status=status.HTTP_400_BAD_REQUEST)

        trends = EconomicIndicator.objects.filter(filters) \
                    .values('year') \
                    .annotate(
                        avg_headline_inflation=Avg('headline_consumer_price_inflation'),
                        avg_food_inflation=Avg('food_consumer_price_inflation'),
                        avg_energy_inflation=Avg('energy_consumer_price_inflation'),
                        avg_core_inflation=Avg('official_core_consumer_price_inflation')
                    ).order_by('year')

        return Response(list(trends))
    except Exception as e:
        print(f"Error in inflation_trends: {e}")
        return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def correlation_analysis(request):
    try:
        pca_insights = CHART_CONFIGURATIONS.get('pca_analysis', {}).get('insights', [])
        pca_loadings = CHART_CONFIGURATIONS.get('pca_analysis', {}).get('components_loading', {})

        static_correlation_matrix = {
            'headers': ['headline_inflation', 'happiness_score', 'gdp_per_capita', 'social_support'],
            'matrix': [
                [1.00, -0.25, -0.10, -0.15],
                [-0.25, 1.00,  0.75,  0.65],
                [-0.10,  0.75, 1.00,  0.80],
                [-0.15,  0.65,  0.80, 1.00]
            ],
            'notes': "This is a static placeholder correlation matrix. Dynamic calculation is a future enhancement."
        }

        response_data = {
            'static_correlation_matrix': static_correlation_matrix,
            'pca_insights': pca_insights,
            'pca_loadings': pca_loadings,
            'message': "Correlation analysis endpoint currently returns static data and PCA insights from configuration."
        }
        return Response(response_data)
    except Exception as e:
        print(f"Error in correlation_analysis: {e}")
        return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def real_estate_price_trends_api(request, governorate_id):
    try:
        # Ensure governorate exists
        governorate = get_object_or_404(TunisiaGovernorate, pk=governorate_id)

        prices = RealEstatePrices.objects.filter(governorate=governorate).order_by('year')

        if not prices.exists():
            return Response({
                'years': [],
                'residential_prices': [],
                'commercial_prices': [],
                'land_prices': []
            }, status=status.HTTP_200_OK)

        years = [price.year for price in prices]
        residential_prices = [price.residential_price_per_m2 for price in prices]
        commercial_prices = [price.commercial_price_per_m2 for price in prices]
        land_prices = [price.land_price_per_m2 for price in prices]

        return Response({
            'governorate_name': governorate.name,
            'years': years,
            'residential_prices': residential_prices,
            'commercial_prices': commercial_prices,
            'land_prices': land_prices
        })
    except TunisiaGovernorate.DoesNotExist:
        return Response({'error': f"Governorate with id {governorate_id} not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error in real_estate_price_trends_api for governorate {governorate_id}: {e}")
        return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def tunisia_map_view(request):
    governorates = TunisiaGovernorate.objects.all().values(
        'id', 'name', 'latitude', 'longitude', 'population_2024', 'unemployment_rate'
    )
    context = {
        'governorates_data': list(governorates)  # Convert QuerySet to list for JSON serialization
    }
    return render(request, 'analytics/tunisia_map.html', context)

@api_view(['GET'])
def labor_market_trends_api(request, governorate_id):
    try:
        governorate = get_object_or_404(TunisiaGovernorate, pk=governorate_id)
        labor_data = LaborMarketData.objects.filter(governorate=governorate).order_by('year')

        if not labor_data.exists():
            return Response({
                'governorate_name': governorate.name, # Return name even if no data
                'years': [],
                'unemployment_rate': [],
                'youth_unemployment': [],
                'female_unemployment': [],
                'labor_force_participation': [],
                'average_wage': [],
                'job_creation_rate': []
            }, status=status.HTTP_200_OK)

        years = [data.year for data in labor_data]
        unemployment_rate = [data.unemployment_rate for data in labor_data]
        youth_unemployment = [data.youth_unemployment for data in labor_data]
        female_unemployment = [data.female_unemployment for data in labor_data]
        labor_force_participation = [data.labor_force_participation for data in labor_data]
        average_wage = [data.average_wage for data in labor_data]
        job_creation_rate = [data.job_creation_rate for data in labor_data]

        return Response({
            'governorate_name': governorate.name,
            'years': years,
            'unemployment_rate': unemployment_rate,
            'youth_unemployment': youth_unemployment,
            'female_unemployment': female_unemployment,
            'labor_force_participation': labor_force_participation,
            'average_wage': average_wage,
            'job_creation_rate': job_creation_rate
        })
    except TunisiaGovernorate.DoesNotExist:
        return Response({'error': f"Governorate with id {governorate_id} not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error in labor_market_trends_api for governorate {governorate_id}: {e}")
        return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def world_map_view(request):
    """Renders the world map page."""
    context = {
        'title': 'World Map'
    }
    return render(request, 'analytics/world_map.html', context)

def investment_advisor_view(request):
    """Renders the investment advisor page."""
    context = {
        'title': 'Investment Advisor'
    }
    return render(request, 'analytics/investment_advisor.html', context)

def country_comparison_page_view(request):
    """Renders the country comparison page."""
    context = {
        'title': 'Country Comparison Tool'
    }
    return render(request, 'countries/country_comparison.html', context)
