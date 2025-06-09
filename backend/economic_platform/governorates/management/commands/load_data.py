import csv
import sys
import traceback
from django.core.management.base import BaseCommand
from django.db import transaction
from governorates.models import Governorate, LaborMarketData

class Command(BaseCommand):
    help = 'Load governorate and labor market data from CSV files'

    def add_arguments(self, parser):
        parser.add_argument('--governorate_csv', type=str, default='newdata/tunisia_gov_data.csv', help='Path to governorate CSV file')
        parser.add_argument('--labor_market_csv', type=str, default='newdata/labor_market_data.csv', help='Path to labor market CSV file')

    @transaction.atomic
    def handle(self, *args, **options):
        # Redirect stdout to capture print statements
        old_stdout = sys.stdout
        sys.stdout = captured_output = sys.stderr

        try:
            # Clear existing data
            print('Clearing existing data...')
            Governorate.objects.all().delete()
            LaborMarketData.objects.all().delete()

            # Load governorate data
            governorate_csv = options['governorate_csv']
            print(f'Loading governorate data from {governorate_csv}...')
            with open(governorate_csv, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        print(f"Processing governorate: {row}")
                        Governorate.objects.create(
                            name=row['name'],
                            arabic_name=row.get('arabic_name', ''),
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
                    except Exception as e:
                        print(f"Error loading governorate: {row}")
                        print(traceback.format_exc())

            # Load labor market data
            labor_market_csv = options['labor_market_csv']
            print(f'Loading labor market data from {labor_market_csv}...')
            with open(labor_market_csv, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        print(f"Processing labor market data: {row}")
                        governorate = Governorate.objects.get(name=row['governorate'])
                        
                        LaborMarketData.objects.create(
                            governorate=governorate,
                            year=int(row['year']),
                            unemployment_rate=float(row['unemployment_rate']),
                            youth_unemployment=float(row['youth_unemployment']),
                            female_unemployment=float(row['female_unemployment']),
                            labor_force_participation=float(row['labor_force_participation']),
                            average_wage=float(row['average_wage']),
                            job_creation_rate=float(row['job_creation_rate']),
                        )
                    except Governorate.DoesNotExist:
                        print(f"Governorate not found: {row['governorate']}")
                        print(traceback.format_exc())
                    except Exception as e:
                        print(f"Error loading labor market data: {row}")
                        print(traceback.format_exc())

            print('Data loading complete!')

        except Exception as e:
            print("Unexpected error during data loading:")
            print(traceback.format_exc())
        finally:
            # Restore stdout
            sys.stdout = old_stdout 