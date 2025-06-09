import csv
from django.core.management.base import BaseCommand
from governorates.models import Governorate, LaborMarketData, RealEstateData

class Command(BaseCommand):
    help = 'Loads governorate, labor market, and real estate data from CSV files.'

    def handle(self, *args, **options):
        self.stdout.write('Loading governorate data...')
        self.load_governorate_data('newdata/tunisia_gov_data.csv')
        self.stdout.write('Governorate data loaded.')

        self.stdout.write('Loading labor market data...')
        self.load_labor_market_data('newdata/labor_market_data.csv')
        self.stdout.write('Labor market data loaded.')

        self.stdout.write('Loading real estate data...')
        self.load_real_estate_data('newdata/real_estate_data.csv')
        self.stdout.write('Real estate data loaded.')

        self.stdout.write(self.style.SUCCESS('Successfully loaded all data.'))

    def load_governorate_data(self, csv_file_path):
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Governorate.objects.create(
                    name=row['name'],
                    arabic_name=row['arabic_name'],
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude']),
                    population_2024=int(row['population_2024']),
                    area_km2=float(row['area_km2']),
                    unemployment_rate=float(row['unemployment_rate']),
                    agricultural_land_percent=float(row['agricultural_land_percent']),
                    population_density=float(row['population_density']),
                    labor_force_size=int(row['labor_force_size']),
                    gdp_contribution=float(row['gdp_contribution']),
                    coastal_access=bool(int(row['coastal_access'])),
                    industrial_zones=int(row['industrial_zones']),
                    tourist_attractions=int(row['tourist_attractions']),
                )

    def load_labor_market_data(self, csv_file_path):
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    governorate = Governorate.objects.get(name=row['governorate'])
                    
                    # Use get_or_create to prevent duplicate entries
                    labor_market_data, created = LaborMarketData.objects.get_or_create(
                        governorate=governorate,
                        year=int(row['year']),
                        defaults={
                            'unemployment_rate': float(row['unemployment_rate']),
                            'youth_unemployment': float(row['youth_unemployment']),
                            'female_unemployment': float(row['female_unemployment']),
                            'labor_force_participation': float(row['labor_force_participation']),
                            'average_wage': float(row['average_wage']),
                            'job_creation_rate': float(row['job_creation_rate']),
                        }
                    )
                    
                    if not created:
                        # If entry already exists, update the values
                        labor_market_data.unemployment_rate = float(row['unemployment_rate'])
                        labor_market_data.youth_unemployment = float(row['youth_unemployment'])
                        labor_market_data.female_unemployment = float(row['female_unemployment'])
                        labor_market_data.labor_force_participation = float(row['labor_force_participation'])
                        labor_market_data.average_wage = float(row['average_wage'])
                        labor_market_data.job_creation_rate = float(row['job_creation_rate'])
                        labor_market_data.save()
                        
                except Governorate.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Governorate not found: {row['governorate']}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing row: {row}, Error: {e}"))

    def load_real_estate_data(self, csv_file_path):
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                governorate = Governorate.objects.get(name=row['governorate'])
                RealEstateData.objects.create(
                    governorate=governorate,
                    year=int(row['year']),
                    residential_price_per_m2=float(row['residential_price_per_m2']),
                    commercial_price_per_m2=float(row['commercial_price_per_m2']),
                    land_price_per_m2=float(row['land_price_per_m2']),
                ) 