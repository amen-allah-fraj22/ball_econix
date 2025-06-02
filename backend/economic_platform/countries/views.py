from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch
from .models import Country, EconomicIndicator
from .serializers import CountryComparisonDataSerializer

class CountryComparisonAPIView(APIView):
    def get(self, request, *args, **kwargs):
        countries_param = request.query_params.get('countries')

        if not countries_param:
            return Response(
                {'error': 'Query parameter "countries" is required. Please provide a comma-separated list of country names.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        country_names = [name.strip() for name in countries_param.split(',')]

        if not country_names:
             return Response(
                {'error': 'Country names list cannot be empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch countries. We will handle missing countries later.
        # We use select_related or prefetch_related if we anticipate accessing related models often in the serializer,
        # but here the serializer's `to_representation` handles fetching the latest indicator.
        # For more complex scenarios or if `latest_economic_indicator` was a direct relation, prefetching would be good.
        # Example:
        # latest_indicator_prefetch = Prefetch(
        #     'economic_indicators',
        #     queryset=EconomicIndicator.objects.order_by('-year'),
        #     to_attr='latest_indicator_list' # a temporary attribute
        # )
        # fetched_countries = Country.objects.filter(name__in=country_names).prefetch_related(latest_indicator_prefetch)

        fetched_countries_qs = Country.objects.filter(name__in=country_names)

        found_country_names = [country.name for country in fetched_countries_qs]
        missing_names = [name for name in country_names if name not in found_country_names]

        # The serializer's to_representation method will handle attaching the latest indicator.
        serializer = CountryComparisonDataSerializer(fetched_countries_qs, many=True)
        serialized_data = serializer.data

        response_data = {
            'comparison_data': serialized_data,
        }

        if missing_names:
            response_data['notes'] = [f"Data for country '{name}' not found." for name in missing_names]
            # Optionally, you could choose to return a 404 if *any* requested country is missing,
            # but returning available data with notes is often more user-friendly.

        return Response(response_data, status=status.HTTP_200_OK)
