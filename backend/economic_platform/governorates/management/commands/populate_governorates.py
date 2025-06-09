from django.core.management.base import BaseCommand
from governorates.models import Governorate

class Command(BaseCommand):
    help = 'Populate Tunisian Governorates'

    def handle(self, *args, **kwargs):
        # Default governorates data
        governorates_data = [
            {
                'name': 'Tunis', 
                'arabic_name': 'تونس',
                'latitude': 36.8065, 
                'longitude': 10.1815, 
                'population_2024': 1200000,
                'area_km2': 300,
                'unemployment_rate': 12.5,
                'agricultural_land_percent': 10,
                'population_density': 4000,
                'labor_force_size': 550000,
                'gdp_contribution': 25.5,
                'coastal_access': True,
                'industrial_zones': 15,
                'tourist_attractions': 20
            },
            {
                'name': 'Ariana', 
                'arabic_name': 'أريانة',
                'latitude': 36.8625, 
                'longitude': 10.1944, 
                'population_2024': 650000,
                'area_km2': 250,
                'unemployment_rate': 11.2,
                'agricultural_land_percent': 15,
                'population_density': 2600,
                'labor_force_size': 300000,
                'gdp_contribution': 12.3,
                'coastal_access': True,
                'industrial_zones': 10,
                'tourist_attractions': 5
            },
            {
                'name': 'Ben Arous', 
                'arabic_name': 'بن عروس',
                'latitude': 36.7472, 
                'longitude': 10.2281, 
                'population_2024': 700000,
                'area_km2': 400,
                'unemployment_rate': 13.8,
                'agricultural_land_percent': 20,
                'population_density': 1750,
                'labor_force_size': 320000,
                'gdp_contribution': 14.2,
                'coastal_access': True,
                'industrial_zones': 12,
                'tourist_attractions': 8
            },
            {
                'name': 'Manouba', 
                'arabic_name': 'منوبة',
                'latitude': 36.8081, 
                'longitude': 10.0969, 
                'population_2024': 420000,
                'area_km2': 250,
                'unemployment_rate': 14.2,
                'agricultural_land_percent': 35,
                'population_density': 1680,
                'labor_force_size': 190000,
                'gdp_contribution': 8.7,
                'coastal_access': False,
                'industrial_zones': 5,
                'tourist_attractions': 3
            },
            {
                'name': 'Nabeul', 
                'arabic_name': 'نابل',
                'latitude': 36.4561, 
                'longitude': 10.7376, 
                'population_2024': 800000,
                'area_km2': 2800,
                'unemployment_rate': 10.9,
                'agricultural_land_percent': 40,
                'population_density': 286,
                'labor_force_size': 360000,
                'gdp_contribution': 11.5,
                'coastal_access': True,
                'industrial_zones': 8,
                'tourist_attractions': 25
            }
        ]

        # Create or update governorates
        for gov_data in governorates_data:
            Governorate.objects.update_or_create(
                name=gov_data['name'],
                defaults=gov_data
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully populated {len(governorates_data)} governorates')) 