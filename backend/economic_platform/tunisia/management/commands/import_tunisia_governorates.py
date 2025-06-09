import csv
import os
from django.core.management.base import BaseCommand
from tunisia.models import TunisiaGovernorate
from django.conf import settings

class Command(BaseCommand):
    help = 'Import Tunisia governorate data from CSV'

    def handle(self, *args, **options):
        csv_file = os.path.join(settings.BASE_DIR.parent.parent, 'newdata', 'tunisia_gov_data.csv')
        
        self.stdout.write(self.style.SUCCESS(f'Attempting to import data from {csv_file}'))
        
        try:
            with open(csv_file, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    TunisiaGovernorate.objects.update_or_create(
                        name=row['name'],
                        defaults={
                            'arabic_name': row['arabic_name'],
                            'latitude': float(row['latitude']),
                            'longitude': float(row['longitude']),
                            'population_2024': int(row['population_2024']),
                            'area_km2': float(row['area_km2']),
                            'unemployment_rate': float(row['unemployment_rate']),
                            'agricultural_land_percent': float(row['agricultural_land_percent']),
                            'population_density': float(row['population_density']),
                            'labor_force_size': int(row['labor_force_size']),
                            'gdp_contribution': float(row['gdp_contribution']),
                            'coastal_access': row['coastal_access'].lower() == 'true',
                            'industrial_zones': int(row['industrial_zones']),
                            'tourist_attractions': int(row['tourist_attractions']),
                        }
                    )
            self.stdout.write(self.style.SUCCESS('Successfully imported governorate data'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: CSV file not found at {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}')) 