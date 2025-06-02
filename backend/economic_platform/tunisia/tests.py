from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import TunisiaGovernorate, InvestmentScore, InvestmentOpportunity # Assuming InvestmentOpportunity might be used or related
from decimal import Decimal

# Helper function to create governorates if needed often
def create_governorate(name, **extra_fields):
    defaults = {
        'population_2024': 1000000,
        'area_km2': 5000,
        'gdp_बिलियन_dinars_2022': Decimal('10.5'),
        'unemployment_rate': Decimal('15.0'),
        'poverty_rate': Decimal('10.0'),
        'foreign_direct_investment_million_dt': Decimal('100.0'),
        'literacy_rate': Decimal('80.0'),
        'human_development_index': Decimal('0.750'),
        'description': f'Description for {name}',
        'advantages': 'Strategic location, skilled labor',
        'challenges': 'Infrastructure needs improvement',
        'key_sectors': 'Agriculture, Tourism',
        'latitude': Decimal('36.8065'), # Default to Tunis latitude
        'longitude': Decimal('10.1815') # Default to Tunis longitude
    }
    defaults.update(extra_fields)
    return TunisiaGovernorate.objects.create(name=name, **defaults)

# Helper function to create investment scores
def create_investment_score(governorate, sector, overall_score, **kwargs):
    defaults = {
        'labor_score': overall_score * Decimal('0.2'),
        'infrastructure_score': overall_score * Decimal('0.2'),
        'tax_incentive_score': overall_score * Decimal('0.2'),
        'market_access_score': overall_score * Decimal('0.2'),
        'economic_stability_score': overall_score * Decimal('0.1'),
        'regulatory_environment_score': overall_score * Decimal('0.1'),
        'reasoning': f'Default reasoning for {sector} in {governorate.name}',
        'last_updated_by_ai': False
    }
    defaults.update(kwargs)
    return InvestmentScore.objects.create(
        governorate=governorate,
        sector=sector,
        overall_score=Decimal(overall_score),
        **defaults
    )

class InvestmentAdvisorAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create Governorates
        cls.gov1 = create_governorate(name="TestGov1", population_2024=500000, area_km2=1000)
        cls.gov2 = create_governorate(name="TestGov2", population_2024=1200000, area_km2=2500)
        cls.gov3 = create_governorate(name="TestGov3", population_2024=800000, area_km2=1500)

        # Create InvestmentScores
        # Sector: Agriculture
        create_investment_score(cls.gov1, InvestmentScore.SECTOR_AGRICULTURE, '0.75', reasoning="Good soil and climate in Gov1 for Agri")
        create_investment_score(cls.gov2, InvestmentScore.SECTOR_AGRICULTURE, '0.60')

        # Sector: Tourism
        create_investment_score(cls.gov1, InvestmentScore.SECTOR_TOURISM, '0.85', reasoning="Gov1 has historical sites")
        create_investment_score(cls.gov3, InvestmentScore.SECTOR_TOURISM, '0.90', reasoning="Gov3 has beautiful beaches and high score")

        # Sector: Technology
        create_investment_score(cls.gov2, InvestmentScore.SECTOR_TECHNOLOGY, '0.92', reasoning="Gov2 tech hub, very high score")
        create_investment_score(cls.gov3, InvestmentScore.SECTOR_TECHNOLOGY, '0.88')

        # Sector: Manufacturing (No scores initially for one test case)

        cls.url = reverse('investment_advisor_api') # from tunisia.urls

    def test_request_with_valid_sector(self):
        """
        Test API request with a valid sector, expecting sorted results.
        """
        response = self.client.get(self.url, {'sector': InvestmentScore.SECTOR_TECHNOLOGY})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Results should be sorted by overall_score descending
        self.assertGreaterEqual(response.data[0]['overall_score'], response.data[1]['overall_score'])
        self.assertEqual(response.data[0]['overall_score'], '0.92') # Gov2
        self.assertEqual(response.data[1]['overall_score'], '0.88') # Gov3
        self.assertEqual(response.data[0]['governorate']['name'], self.gov2.name)

    def test_request_with_valid_sector_and_min_score(self):
        """
        Test API request with a valid sector and min_investment_score.
        """
        response = self.client.get(self.url, {'sector': InvestmentScore.SECTOR_TOURISM, 'min_investment_score': '0.89'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['overall_score'], '0.90')
        self.assertEqual(response.data[0]['governorate']['name'], self.gov3.name)
        self.assertEqual(response.data[0]['reasoning'], "Gov3 has beautiful beaches and high score")

    def test_request_with_sector_no_matching_data(self):
        """
        Test API request with a sector that has no InvestmentScore data.
        """
        response = self.client.get(self.url, {'sector': InvestmentScore.SECTOR_MANUFACTURING})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0) # Expect an empty list

    def test_request_without_sector_parameter(self):
        """
        Test API request without the required 'sector' parameter.
        """
        response = self.client.get(self.url) # No query params
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Sector parameter is required.')

    def test_request_with_invalid_min_investment_score(self):
        """
        Test API request with an invalid (non-numeric) min_investment_score.
        """
        response = self.client.get(self.url, {'sector': InvestmentScore.SECTOR_AGRICULTURE, 'min_investment_score': 'not-a-number'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid min_investment_score. Must be a number.')

    def test_serializer_content_check(self):
        """
        Check the content of serialized data for one item.
        """
        response = self.client.get(self.url, {'sector': InvestmentScore.SECTOR_TOURISM, 'min_investment_score': '0.86'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        item = response.data[0]
        self.assertEqual(item['sector'], InvestmentScore.SECTOR_TOURISM)
        self.assertEqual(item['overall_score'], '0.90')
        self.assertEqual(item['labor_score'], '0.18') # 0.90 * 0.2
        self.assertEqual(item['infrastructure_score'], '0.18') # 0.90 * 0.2
        self.assertEqual(item['tax_incentive_score'], '0.18') # 0.90 * 0.2
        self.assertEqual(item['market_access_score'], '0.18') # 0.90 * 0.2
        self.assertEqual(item['reasoning'], "Gov3 has beautiful beaches and high score")

        governorate_data = item['governorate']
        self.assertEqual(governorate_data['name'], self.gov3.name)
        self.assertEqual(governorate_data['population_2024'], 800000)
        self.assertEqual(governorate_data['area_km2'], 1500)

    def test_case_insensitivity_for_sector(self):
        """
        Test that the sector filter is case-insensitive.
        """
        response = self.client.get(self.url, {'sector': 'agriculture'}) # Lowercase
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Check if results for 'Agriculture' are returned
        sectors_in_response = {item['sector'] for item in response.data}
        self.assertIn(InvestmentScore.SECTOR_AGRICULTURE, sectors_in_response)

        response_upper = self.client.get(self.url, {'sector': 'TECHNOLOGY'}) # Uppercase
        self.assertEqual(response_upper.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_upper.data), 2)
        sectors_in_response_upper = {item['sector'] for item in response_upper.data}
        self.assertIn(InvestmentScore.SECTOR_TECHNOLOGY, sectors_in_response_upper)

    def test_min_score_boundary_conditions(self):
        """
        Test min_investment_score with boundary conditions (equal to a score).
        """
        # Score exactly equal to an existing item
        response = self.client.get(self.url, {'sector': InvestmentScore.SECTOR_AGRICULTURE, 'min_investment_score': '0.75'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['overall_score'], '0.75')

        # Score just above an existing item
        response = self.client.get(self.url, {'sector': InvestmentScore.SECTOR_AGRICULTURE, 'min_investment_score': '0.751'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        # Score just below an existing item
        response = self.client.get(self.url, {'sector': InvestmentScore.SECTOR_AGRICULTURE, 'min_investment_score': '0.749'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['overall_score'], '0.75')

    def test_empty_sector_parameter(self):
        """
        Test API request with an empty 'sector' parameter.
        """
        response = self.client.get(self.url, {'sector': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Sector parameter is required.')

print("Finished defining InvestmentAdvisorAPIViewTests")

# Note: Django's test runner will discover this file and the APITestCase class.
# To run these tests, you would typically use:
# python manage.py test backend.economic_platform.tunisia
# Or, if your apps are structured differently in settings.py:
# python manage.py test tunisia
# Or run all tests:
# python manage.py test
#
# Make sure the `tunisia` app is in INSTALLED_APPS in your settings.py
# and that the database is configured for testing (usually handled automatically by Django).
# Also, ensure models.py has InvestmentScore.SECTOR_CHOICES defined correctly if you are using them.
# For example, SECTOR_AGRICULTURE = "Agriculture"
# SECTOR_TOURISM = "Tourism", etc. in the InvestmentScore model.
# The test data setup assumes these string values for sectors.
# The `InvestmentOpportunity` model was imported but not used; can be removed if not needed.
# The helper functions `create_governorate` and `create_investment_score` are good practice.
# The `Decimal` type is correctly used for monetary values and rates.
# The URL name 'investment_advisor_api' must match what's in tunisia.urls.py.
# `setUpTestData` is used, which is efficient for test data that doesn't change per test method.
# The print statement at the end is just for confirmation during generation and won't affect tests.
