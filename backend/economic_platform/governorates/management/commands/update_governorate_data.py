import pandas as pd
from django.core.management.base import BaseCommand
from governorates.models import Governorate

class Command(BaseCommand):
    help = 'Update governorate data from CSV file'

    def handle(self, *args, **options):
        # Read the CSV file
        try:
            df = pd.read_csv('newdata/tunisia_gov_data.csv')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading CSV file: {e}'))
            return

        # Track updates
        updates_count = 0
        creates_count = 0

        # Iterate through each row and update governorate data
        for _, row in df.iterrows():
            try:
                # Try to find the existing governorate or create a new one
                governorate, created = Governorate.objects.update_or_create(
                    name=row['name'],
                    defaults={
                        'arabic_name': row['arabic_name'],
                        'latitude': row['latitude'],
                        'longitude': row['longitude'],
                        'population_2024': row['population_2024'],
                        'area_km2': row['area_km2'],
                        'unemployment_rate': row['unemployment_rate'],
                        'agricultural_land_percent': row['agricultural_land_percent'],
                        'population_density': row['population_density'],
                        'labor_force_size': row['labor_force_size'],
                        'gdp_contribution': row['gdp_contribution'],
                        'coastal_access': bool(row['coastal_access']),
                        'industrial_zones': row['industrial_zones'],
                        'tourist_attractions': row['tourist_attractions']
                    }
                )
                
                if created:
                    creates_count += 1
                else:
                    updates_count += 1
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing governorate {row["name"]}: {e}'))

        # Final output
        self.stdout.write(self.style.SUCCESS(f'Created {creates_count} new governorates.'))
        self.stdout.write(self.style.SUCCESS(f'Updated {updates_count} existing governorates.')) 