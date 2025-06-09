from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from countries.models import Country, EconomicIndicator
from tunisia.models import RealEstatePrices, TunisiaGovernorate, InvestmentScore
from governorates.models import Sector, RecommendationDetails, Governorate, LaborMarketData, RealEstateData
from .chart_configs import CHART_CONFIGURATIONS
from django.db.models import Max, F, Q, Avg
from django.db.models.functions import ExtractYear
from django.shortcuts import get_object_or_404, render
import pandas as pd
from rest_framework.permissions import AllowAny
import json
from countries.serializers import CountrySerializer
from governorates.serializers import RecommendationDetailsSerializer, GovernorateSerializer, LaborMarketDataSerializer, RealEstateDataSerializer

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
    print("DEBUG: global_dashboard_data function entered.")
    try:
        latest_year_data = EconomicIndicator.objects.aggregate(latest_year=Max('year'))
        latest_year = latest_year_data.get('latest_year')

        if not latest_year:
            print("DEBUG: global_dashboard_data - No latest year found.")
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

        print(f"DEBUG: global_dashboard_data - Number of countries with happiness data: {countries_with_happiness.count()}")

        formatted_data = []
        for country_data in countries_with_happiness:
            formatted_data.append({
                'country': country_data['name'],
                'happiness': country_data['latest_happiness_score'],
                'lat': country_data['latitude'],
                'lng': country_data['longitude'],
                'code': country_data['code']
            })

        print("DEBUG: global_dashboard_data - Formatted data prepared:", formatted_data)
        return Response(formatted_data)
    except Exception as e:
        print(f"Error in global_dashboard_data: {e}")
        return Response({'error': 'An unexpected error occurred. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def search_countries(request):
    query = request.query_params.get('q', None)
    if not query:
        return Response([], status=status.HTTP_200_OK)

    try:
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
            # Get the latest EconomicIndicator for the current country
            latest_indicator = EconomicIndicator.objects.filter(
                country=country,
                happiness_score__isnull=False
            ).order_by('-year').first() # Order by year descending to get the latest

            if latest_indicator:
                data['happiness_score'] = latest_indicator.happiness_score
            results.append(data)

        results.sort(key=lambda x: (
            (x['code'].lower() if x['code'] else '') != query.lower(),
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

        print(f"DEBUG: inflation_trends - Data: {list(trends)}") # Debug print
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
        print(f"DEBUG: correlation_analysis - Data: {response_data}") # Debug print
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
    try:
        governorates = TunisiaGovernorate.objects.all().values(
            'id', 'name', 'latitude', 'longitude', 'population_2024', 'unemployment_rate'
        )
        context = {
            'governorates_data_json': json.dumps(list(governorates)) # Serialize to JSON string
        }
        return render(request, 'analytics/tunisia_map.html', context)
    except Exception as e:
        print(f"Error in tunisia_map_view: {e}")
        # You might want to render an error page or return an empty context
        return render(request, 'analytics/tunisia_map.html', {'error_message': f'Failed to load Tunisia map data: {e}'}) # Or handle this more gracefully

@api_view(['GET'])
def labor_market_trends_api(request, governorate_id):
    try:
        # Use get_object_or_404 to handle non-existent governorate
        governorate = get_object_or_404(Governorate, pk=governorate_id)
        
        # Fetch labor market data for the specific governorate, ordered by year
        labor_data = LaborMarketData.objects.filter(governorate=governorate).order_by('year')

        # If no data exists, return a response with empty lists but governorate name
        if not labor_data.exists():
            return Response({
                'governorate_name': governorate.name,
                'years': [],
                'unemployment_rate': [],
                'youth_unemployment': [],
                'female_unemployment': [],
                'labor_force_participation': [],
                'average_wage': [],
                'job_creation_rate': []
            }, status=status.HTTP_200_OK)

        # Extract data into lists
        years = [data.year for data in labor_data]
        unemployment_rate = [data.unemployment_rate for data in labor_data]
        youth_unemployment = [data.youth_unemployment for data in labor_data]
        female_unemployment = [data.female_unemployment for data in labor_data]
        labor_force_participation = [data.labor_force_participation for data in labor_data]
        average_wage = [data.average_wage for data in labor_data]
        job_creation_rate = [data.job_creation_rate for data in labor_data]

        # Return the data
        return Response({
            'governorate_name': governorate.name,
            'years': years,
            'unemployment_rate': unemployment_rate,
            'youth_unemployment': youth_unemployment,
            'female_unemployment': female_unemployment,
            'labor_force_participation': labor_force_participation,
            'average_wage': average_wage,
            'job_creation_rate': job_creation_rate
        }, status=status.HTTP_200_OK)

    except Governorate.DoesNotExist:
        return Response({
            'error': f"Governorate with id {governorate_id} not found.",
            'governorate_name': None,
            'years': [],
            'unemployment_rate': [],
            'youth_unemployment': [],
            'female_unemployment': [],
            'labor_force_participation': [],
            'average_wage': [],
            'job_creation_rate': []
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        # Log the full error for server-side debugging
        print(f"Unexpected error in labor_market_trends_api: {type(e).__name__} - {e}")
        
        return Response({
            'error': 'An unexpected error occurred while fetching labor market data.',
            'governorate_name': None,
            'years': [],
            'unemployment_rate': [],
            'youth_unemployment': [],
            'female_unemployment': [],
            'labor_force_participation': [],
            'average_wage': [],
            'job_creation_rate': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def world_map_view(request):
    """Renders the world map page."""
    context = {
        'title': 'World Map'
    }
    return render(request, 'analytics/world_map.html', context)

@api_view(['GET'])
@permission_classes([AllowAny])
def world_map_data(request):
    """API endpoint to provide data for the world map, including happiness and inflation."""
    try:
        # Fetch all countries that have valid latitude and longitude
        countries = Country.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).distinct() # Use distinct to avoid duplicates if countries have multiple related objects

        map_data = []
        for country in countries:
            # Try to get the latest economic indicator for each country
            latest_indicator = EconomicIndicator.objects.filter(
                country=country
            ).order_by('-year').first()

            if latest_indicator: # Only add if there is a corresponding economic indicator
                map_data.append({
                    'name': country.name,
                    'code': country.code, # Ensure Country model has a 'code' field
                    'latitude': country.latitude,
                    'longitude': country.longitude,
                    'happiness_score': latest_indicator.happiness_score if latest_indicator.happiness_score is not None else 'N/A',
                    'inflation_rate': latest_indicator.headline_consumer_price_inflation if latest_indicator.headline_consumer_price_inflation is not None else 'N/A',
                })
        return Response(map_data)
    except Exception as e:
        print(f"Error in world_map_data: {e}")
        return Response({'error': f'An unexpected error occurred while fetching map data: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_investment_recommendation(request):
    sector = request.query_params.get('sector', None)
    if not sector:
        return Response({'error': 'Sector parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch investment scores for the given sector, ordered by overall_score descending
        recommendations = InvestmentScore.objects.filter(
            sector__iexact=sector
        ).order_by('-overall_score').select_related('governorate')

        if not recommendations.exists():
            # If no actual data, return a generic message
            return Response({'message': 'No specific recommendations found for this sector. Consider investing generally in regions with good infrastructure and a skilled labor force.'},
                            status=status.HTTP_200_OK)

        formatted_recommendations = []
        for rec in recommendations:
            formatted_recommendations.append({
                'governorate_name': rec.governorate.name,
                'overall_score': rec.overall_score,
                'reasoning': rec.reasoning,
                'latitude': rec.governorate.latitude,
                'longitude': rec.governorate.longitude,
            })

        # For simplicity, returning top 3 recommendations
        return Response(formatted_recommendations[:3])

    except Exception as e:
        print(f"Error fetching investment recommendation: {e}")
        return Response({'error': 'An unexpected error occurred while fetching recommendations.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Static recommendations for demonstration purposes
STATIC_RECOMMENDATIONS = {
    "tech": [
        {
            "governorate": {"name": "Tunis", "latitude": 36.8065, "longitude": 10.1815},
            "recommendation_details": {
                "contact_info_investment_offices": "Invest in Tunisia Agency (FIPA) - Tech Desk",
                "relevant_government_agencies": "Ministry of Digital Economy",
                "required_permits_procedures": "Business registration, tech park permits",
                "timeline_for_setup": "3-6 months",
                "investment_size_recommendations": "Medium to Large (>$500k)",
                "infrastructure_details": "High-speed internet, growing tech hubs, incubators like Technopark El Ghazala.",
                "economic_incentives": "Tax exemptions for startups, R&D grants, special tech park benefits.",
                "geographic_advantages": "Proximity to Europe, skilled young workforce, multilingual talent.",
                "cost_analysis_summary": "Lower operating costs compared to Europe, competitive salaries.",
                "success_stories": "Several successful Tunisian tech startups expanding internationally.",
            },
            "ranking_score": 95,
            "labor_market_data": None,
            "real_estate_data": None,
        },
        {
            "governorate": {"name": "Sfax", "latitude": 34.7406, "longitude": 10.7603},
            "recommendation_details": {
                "contact_info_investment_offices": "Sfax Chamber of Commerce - Tech Sector",
                "relevant_government_agencies": "Ministry of Digital Economy",
                "required_permits_procedures": "Standard business registration",
                "timeline_for_setup": "4-7 months",
                "investment_size_recommendations": "Medium (>$200k)",
                "infrastructure_details": "Good university presence, emerging tech community.",
                "economic_incentives": "Regional development incentives.",
                "geographic_advantages": "Strong academic ecosystem, access to southern markets.",
                "cost_analysis_summary": "Affordable talent pool, lower rental costs.",
                "success_stories": "Growing number of IT service companies.",
            },
            "ranking_score": 88,
            "labor_market_data": None,
            "real_estate_data": None,
        }
    ],
    "agriculture": [
        {
            "governorate": {"name": "Kairouan", "latitude": 35.6781, "longitude": 10.0963},
            "recommendation_details": {
                "contact_info_investment_offices": "Regional Agricultural Development Commissioner (CRDA) - Kairouan",
                "relevant_government_agencies": "Ministry of Agriculture",
                "required_permits_procedures": "Land acquisition permits, agricultural operating licenses.",
                "timeline_for_setup": "6-12 months",
                "investment_size_recommendations": "Large (>$1M) for large-scale farming.",
                "infrastructure_details": "Vast agricultural lands, irrigation systems in place.",
                "economic_incentives": "Subsidies for agricultural equipment, tax breaks for new farms, water management support.",
                "geographic_advantages": "Fertile lands, suitable climate for various crops (olives, cereals, vegetables).",
                "cost_analysis_summary": "Competitive land prices, available rural labor.",
                "success_stories": "Success in olive oil production and organic farming.",
            },
            "ranking_score": 92,
            "labor_market_data": None,
            "real_estate_data": None,
        },
        {
            "governorate": {"name": "Nabeul", "latitude": 36.4561, "longitude": 10.7376},
            "recommendation_details": {
                "contact_info_investment_offices": "CRDA - Nabeul",
                "relevant_government_agencies": "Ministry of Agriculture",
                "required_permits_procedures": "Standard agricultural permits.",
                "timeline_for_setup": "5-10 months",
                "investment_size_recommendations": "Medium to Large (>$500k).",
                "infrastructure_details": "Well-established agricultural infrastructure, proximity to ports for export.",
                "economic_incentives": "Support for high-value crops (citrus, flowers).",
                "geographic_advantages": "Coastal access, diverse agricultural production.",
                "cost_analysis_summary": "Good market access, established supply chains.",
                "success_stories": "Leader in citrus fruits and flower exports.",
            },
            "ranking_score": 89,
            "labor_market_data": None,
            "real_estate_data": None,
        }
    ],
    "tourism": [
        {
            "governorate": {"name": "Sousse", "latitude": 35.8256, "longitude": 10.6369},
            "recommendation_details": {
                "contact_info_investment_offices": "National Tourist Office (ONTT) - Sousse",
                "relevant_government_agencies": "Ministry of Tourism",
                "required_permits_procedures": "Hotel licenses, tourism facility permits.",
                "timeline_for_setup": "12-24 months for large projects.",
                "investment_size_recommendations": "Large (>$2M) for hotel development.",
                "infrastructure_details": "Developed tourism infrastructure, international airport, well-known resorts.",
                "economic_incentives": "Investment grants for tourism projects, tax benefits, facilitated access to financing.",
                "geographic_advantages": "Beautiful beaches, historical sites, strong existing tourist flow.",
                "cost_analysis_summary": "Established market, good return on investment for well-managed properties.",
                "success_stories": "One of Tunisia's leading tourist destinations.",
            },
            "ranking_score": 98,
            "labor_market_data": None,
            "real_estate_data": None,
        },
        {
            "governorate": {"name": "Medenine", "latitude": 33.3548, "longitude": 10.5055},
            "recommendation_details": {
                "contact_info_investment_offices": "ONTT - Djerba/Medenine",
                "relevant_government_agencies": "Ministry of Tourism",
                "required_permits_procedures": "Standard tourism permits.",
                "timeline_for_setup": "10-18 months.",
                "investment_size_recommendations": "Medium to Large (>$1M).",
                "infrastructure_details": "Unique island charm, international airport, cultural heritage sites.",
                "economic_incentives": "Specific incentives for island tourism development.",
                "geographic_advantages": "Unique landscape, cultural tourism potential, strong appeal to specific niches.",
                "cost_analysis_summary": "Higher seasonality but strong niche market.",
                "success_stories": "Renowned for its unique cultural and seaside tourism.",
            },
            "ranking_score": 90,
            "labor_market_data": None,
            "real_estate_data": None,
        }
    ],
    "manufacturing": [
        {
            "governorate": {"name": "Ben Arous", "latitude": 36.7472, "longitude": 10.2281},
            "recommendation_details": {
                "contact_info_investment_offices": "API (Agency for the Promotion of Industry and Innovation) - Ben Arous",
                "relevant_government_agencies": "Ministry of Industry",
                "required_permits_procedures": "Industrial operating licenses, environmental permits.",
                "timeline_for_setup": "6-12 months.",
                "investment_size_recommendations": "Medium to Large (>$750k).",
                "infrastructure_details": "Well-developed industrial zones, proximity to Tunis port and airport.",
                "economic_incentives": "Tax incentives for export-oriented industries, investment premiums.",
                "geographic_advantages": "Strategic location, excellent logistics access.",
                "cost_analysis_summary": "Competitive labor costs, established industrial ecosystem.",
                "success_stories": "Strong automotive components and textile industries.",
            },
            "ranking_score": 93,
            "labor_market_data": None,
            "real_estate_data": None,
        },
        {
            "governorate": {"name": "Monastir", "latitude": 35.7643, "longitude": 10.8265},
            "recommendation_details": {
                "contact_info_investment_offices": "API - Monastir",
                "relevant_government_agencies": "Ministry of Industry",
                "required_permits_procedures": "Standard industrial permits.",
                "timeline_for_setup": "7-14 months.",
                "investment_size_recommendations": "Medium (>$400k).",
                "infrastructure_details": "Textile and clothing industrial zones, international airport.",
                "economic_incentives": "Support for innovative manufacturing processes.",
                "geographic_advantages": "Strong legacy in textile industry, skilled workforce.",
                "cost_analysis_summary": "Established industry, competitive labor costs.",
                "success_stories": "A hub for textile and apparel manufacturing.",
            },
            "ranking_score": 87,
            "labor_market_data": None,
            "real_estate_data": None,
        }
    ]
}

def investment_recommendations_view(request, sector):
    # Normalize the sector name for consistent lookup
    sector_mapping = {
        "tech": "tech",
        "technology": "tech", # Map 'technology' to 'tech'
        "agriculture": "agriculture",
        "tourism": "tourism",
        "manifacturing": "manufacturing", # Corrected typo for 'manufacturing'
        "manufacturing": "manufacturing",
    }
    normalized_sector = sector_mapping.get(sector.lower(), sector.lower())

    recommendation_data = []
    sector_obj = None
    
    try:
        sector_obj = Sector.objects.get(name__iexact=sector)
    except Sector.DoesNotExist:
        pass # We will handle the case where sector_obj is None below

    if sector_obj:
        recommendations = RecommendationDetails.objects.filter(sector=sector_obj).select_related('governorate')
        if recommendations.exists():
            for rec in recommendations:
                governorate = rec.governorate
                labor_data = LaborMarketData.objects.filter(governorate=governorate).order_by('-year').first()
                real_estate_data = RealEstateData.objects.filter(governorate=governorate).order_by('-year').first()

                recommendation_data.append({
                    'governorate': GovernorateSerializer(governorate).data,
                    'recommendation_details': RecommendationDetailsSerializer(rec).data,
                    'labor_market_data': LaborMarketDataSerializer(labor_data).data if labor_data else None,
                    'real_estate_data': RealEstateDataSerializer(real_estate_data).data if real_estate_data else None,
                    'ranking_score': rec.ranking_score,
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
            # Sort recommendations by ranking score if real data exists
            recommendation_data = sorted(recommendation_data, key=lambda x: x.get('ranking_score', 0) or 0, reverse=True)
    
    if not recommendation_data: # If no real data or sector_obj was not found
        static_recs = STATIC_RECOMMENDATIONS.get(normalized_sector)
        if static_recs:
            recommendation_data = static_recs
        else:
            # If no static data either, return the original error message
            context = {
                'sector_name': sector,
                'error_message': f'No recommendations found for the {sector} sector.'
            }
            return render(request, 'analytics/investment_recommendations_page.html', context)

    context = {
        'sector_name': sector,
        'recommendations': recommendation_data,
    }
    return render(request, 'analytics/investment_recommendations_page.html', context)
