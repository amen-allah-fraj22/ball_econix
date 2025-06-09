import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'economic_platform.settings')
django.setup()

import csv
from governorates.models import Governorate, LaborMarketData

def load_governorate_data(csv_file_path):
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Governorate.objects.get_or_create(
                name=row['name'],
                defaults={
                    'arabic_name': row.get('arabic_name', ''),
                    'latitude': float(row['latitude']),
                    'longitude': float(row['longitude']),
                    'population_2024': int(row['population_2024']),
                    'area_km2': float(row['area_km2']),
                    'unemployment_rate': float(row['unemployment_rate']),
                    'agricultural_land_percent': float(row['agricultural_land_percent']),
                    'population_density': float(row['population_density']),
                    'labor_force_size': int(row['labor_force_size']),
                    'gdp_contribution': float(row['gdp_contribution']),
                    'coastal_access': bool(int(row['coastal_access'])),
                    'industrial_zones': int(row['industrial_zones']),
                    'tourist_attractions': int(row['tourist_attractions']),
                }
            )

def load_labor_market_data(csv_file_path):
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
                print(f"Governorate not found: {row['governorate']}")
            except Exception as e:
                print(f"Error processing row: {row}, Error: {e}")

def main():
    # Clear existing data
    Governorate.objects.all().delete()
    LaborMarketData.objects.all().delete()
    
    # Load new data
    load_governorate_data('newdata/tunisia_gov_data.csv')
    load_labor_market_data('newdata/labor_market_data.csv')
    
    print("Data loading complete!")

if __name__ == '__main__':
    main() 