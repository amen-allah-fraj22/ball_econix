import os
import sys
import django
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('governorate_update.log'),
                        logging.StreamHandler(sys.stdout)
                    ])

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'economic_platform.settings')
django.setup()

from governorates.models import Governorate

def update_governorate_data():
    try:
        # Read the CSV file
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'newdata', 'tunisia_gov_data.csv')
        
        # Verify CSV file exists
        if not os.path.exists(csv_path):
            logging.error(f"CSV file not found at {csv_path}")
            return
        
        # Read CSV with error handling
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            logging.error(f"Error reading CSV file: {e}")
            return
        
        # Validate required columns
        required_columns = [
            'name', 'arabic_name', 'latitude', 'longitude', 
            'population_2024', 'area_km2', 'unemployment_rate', 
            'agricultural_land_percent', 'population_density', 
            'labor_force_size', 'gdp_contribution', 'coastal_access', 
            'industrial_zones', 'tourist_attractions'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logging.error(f"Missing columns in CSV: {missing_columns}")
            return
        
        # Track updates
        updates_count = 0
        creates_count = 0
        
        # Iterate through each row and update governorate data
        for _, row in df.iterrows():
            try:
                # Try to find the existing governorate or create a new one
                governorate, created = Governorate.objects.get_or_create(
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
                
                # If the governorate already exists, update its fields
                if not created:
                    governorate.arabic_name = row['arabic_name']
                    governorate.latitude = row['latitude']
                    governorate.longitude = row['longitude']
                    governorate.population_2024 = row['population_2024']
                    governorate.area_km2 = row['area_km2']
                    governorate.unemployment_rate = row['unemployment_rate']
                    governorate.agricultural_land_percent = row['agricultural_land_percent']
                    governorate.population_density = row['population_density']
                    governorate.labor_force_size = row['labor_force_size']
                    governorate.gdp_contribution = row['gdp_contribution']
                    governorate.coastal_access = bool(row['coastal_access'])
                    governorate.industrial_zones = row['industrial_zones']
                    governorate.tourist_attractions = row['tourist_attractions']
                    governorate.save()
                    updates_count += 1
                else:
                    creates_count += 1
            
            except Exception as e:
                logging.error(f"Error processing governorate {row['name']}: {e}")
        
        # Final logging
        logging.info(f"Governorate data update complete.")
        logging.info(f"Created {creates_count} new governorates.")
        logging.info(f"Updated {updates_count} existing governorates.")
    
    except Exception as e:
        logging.error(f"Unexpected error in update process: {e}")

if __name__ == '__main__':
    update_governorate_data() 