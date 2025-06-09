import os
import sys
import traceback

# Determine the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend', 'economic_platform'))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'economic_platform.settings')

try:
    import django
    django.setup()
except Exception as e:
    print(f"Django setup error: {e}")
    print(traceback.format_exc())
    sys.exit(1)

import csv
from governorates.models import Governorate, LaborMarketData

def load_governorate_data(csv_file_path):
    print(f"Loading governorate data from {csv_file_path}")
    governorates_created = 0
    
    try:
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    governorate, created = Governorate.objects.get_or_create(
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
                    
                    if created:
                        governorates_created += 1
                        print(f"Created governorate: {governorate.name}")
                
                except Exception as e:
                    print(f"Error processing governorate row: {row}")
                    print(traceback.format_exc())
        
        print(f"Total governorates created: {governorates_created}")
        return governorates_created
    
    except FileNotFoundError:
        print(f"CSV file not found: {csv_file_path}")
        return 0
    except Exception as e:
        print(f"Unexpected error loading governorate data: {e}")
        print(traceback.format_exc())
        return 0

def load_labor_market_data(csv_file_path):
    print(f"Loading labor market data from {csv_file_path}")
    labor_data_created = 0
    
    try:
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    governorate = Governorate.objects.get(name=row['governorate'])
                    
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
                    
                    if created:
                        labor_data_created += 1
                        print(f"Created labor market data for {governorate.name} - {labor_market_data.year}")
                
                except Governorate.DoesNotExist:
                    print(f"Governorate not found: {row['governorate']}")
                except Exception as e:
                    print(f"Error processing labor market data row: {row}")
                    print(traceback.format_exc())
        
        print(f"Total labor market data entries created: {labor_data_created}")
        return labor_data_created
    
    except FileNotFoundError:
        print(f"CSV file not found: {csv_file_path}")
        return 0
    except Exception as e:
        print(f"Unexpected error loading labor market data: {e}")
        print(traceback.format_exc())
        return 0

def main():
    # Clear existing data
    print("Clearing existing data...")
    try:
        Governorate.objects.all().delete()
        LaborMarketData.objects.all().delete()
    except Exception as e:
        print(f"Error clearing data: {e}")
        print(traceback.format_exc())
        return
    
    # Load new data
    governorate_csv = os.path.join(project_root, 'newdata', 'tunisia_gov_data.csv')
    labor_market_csv = os.path.join(project_root, 'newdata', 'labor_market_data.csv')
    
    print(f"Governorate CSV path: {governorate_csv}")
    print(f"Labor Market CSV path: {labor_market_csv}")
    
    governorates_count = load_governorate_data(governorate_csv)
    labor_data_count = load_labor_market_data(labor_market_csv)
    
    print(f"\nData Loading Summary:")
    print(f"Governorates: {governorates_count}")
    print(f"Labor Market Data Entries: {labor_data_count}")

if __name__ == '__main__':
    main() 