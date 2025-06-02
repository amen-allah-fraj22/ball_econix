import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from tunisia.models import TunisiaGovernorate, RealEstatePrices, LaborMarketData

# Helper function to convert empty strings to None for numeric fields
def to_int_or_none(value):
    if value == '':
        return None
    try:
        return int(value)
    except ValueError:
        return None # Or raise an error, or log it

def to_float_or_none(value):
    if value == '':
        return None
    try:
        return float(value)
    except ValueError:
        return None # Or raise an error, or log it

def to_bool(value):
    return value == '1'

class Command(BaseCommand):
    help = 'Populates Tunisia-specific data from text files in the newdata directory'

    def handle(self, *args, **options):
        # Construct paths relative to the project's root directory
        # settings.BASE_DIR is backend/economic_platform/
        project_root = settings.BASE_DIR.parent.parent
        gov_data_path = project_root / 'newdata' / 'tunisia_gov_data.txt'
        real_estate_data_path = project_root / 'newdata' / 'real_estate_data.txt'
        labor_market_data_path = project_root / 'newdata' / 'labor_market_data.txt'

        self.stdout.write("Starting data population process...")

        # Populate TunisiaGovernorate
        self.stdout.write(f"Populating TunisiaGovernorate from {gov_data_path}...")
        try:
            with open(gov_data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0
                for row in reader:
                    try:
                        governorate, created = TunisiaGovernorate.objects.update_or_create(
                            name=row['name'],
                            defaults={
                                'arabic_name': row.get('arabic_name', ''),
                                'latitude': to_float_or_none(row.get('latitude')),
                                'longitude': to_float_or_none(row.get('longitude')),
                                'population_2024': to_int_or_none(row.get('population_2024')),
                                'area_km2': to_float_or_none(row.get('area_km2')),
                                'unemployment_rate': to_float_or_none(row.get('unemployment_rate')),
                                'agricultural_land_percent': to_float_or_none(row.get('agricultural_land_percent')),
                                'population_density': to_float_or_none(row.get('population_density')),
                                'labor_force_size': to_int_or_none(row.get('labor_force_size')),
                                'gdp_contribution': to_float_or_none(row.get('gdp_contribution')),
                                'coastal_access': to_bool(row.get('coastal_access')),
                                'industrial_zones': to_int_or_none(row.get('industrial_zones')),
                                'tourist_attractions': to_int_or_none(row.get('tourist_attractions')),
                            }
                        )
                        count += 1
                        if created:
                            self.stdout.write(self.style.SUCCESS(f"Created governorate: {governorate.name}"))
                        else:
                            self.stdout.write(f"Updated governorate: {governorate.name}")
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error processing row for {row.get('name', 'Unknown Governorate')}: {e} - Row: {row}"))
                self.stdout.write(self.style.SUCCESS(f"Processed {count} governorate records."))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {gov_data_path}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred while populating TunisiaGovernorate: {e}"))

        # Populate RealEstatePrices
        self.stdout.write(f"Populating RealEstatePrices from {real_estate_data_path}...")
        try:
            with open(real_estate_data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0
                for row in reader:
                    try:
                        governorate_name = row.get('governorate')
                        year = to_int_or_none(row.get('year'))
                        if not governorate_name or year is None:
                            self.stderr.write(self.style.WARNING(f"Skipping row due to missing governorate or year: {row}"))
                            continue
                        
                        governorate = TunisiaGovernorate.objects.get(name=governorate_name)
                        price_data, created = RealEstatePrices.objects.update_or_create(
                            governorate=governorate,
                            year=year,
                            defaults={
                                'residential_price_per_m2': to_float_or_none(row.get('residential_price_per_m2')),
                                'commercial_price_per_m2': to_float_or_none(row.get('commercial_price_per_m2')),
                                'land_price_per_m2': to_float_or_none(row.get('land_price_per_m2')),
                            }
                        )
                        count += 1
                        # if created:
                        #     self.stdout.write(self.style.SUCCESS(f"Created real estate data for {governorate.name} - {year}"))
                        # else:
                        #     self.stdout.write(f"Updated real estate data for {governorate.name} - {year}")
                    except TunisiaGovernorate.DoesNotExist:
                        self.stderr.write(self.style.ERROR(f"Governorate '{governorate_name}' not found for real estate data. Row: {row}"))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error processing real estate row for {governorate_name} - {year}: {e} - Row: {row}"))
                self.stdout.write(self.style.SUCCESS(f"Processed {count} real estate price records."))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {real_estate_data_path}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred while populating RealEstatePrices: {e}"))


        # Populate LaborMarketData
        self.stdout.write(f"Populating LaborMarketData from {labor_market_data_path}...")
        try:
            with open(labor_market_data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0
                for row in reader:
                    try:
                        governorate_name = row.get('governorate')
                        year = to_int_or_none(row.get('year'))
                        if not governorate_name or year is None:
                            self.stderr.write(self.style.WARNING(f"Skipping row due to missing governorate or year: {row}"))
                            continue

                        governorate = TunisiaGovernorate.objects.get(name=governorate_name)
                        labor_data, created = LaborMarketData.objects.update_or_create(
                            governorate=governorate,
                            year=year,
                            defaults={
                                'unemployment_rate': to_float_or_none(row.get('unemployment_rate')),
                                'youth_unemployment': to_float_or_none(row.get('youth_unemployment')),
                                'female_unemployment': to_float_or_none(row.get('female_unemployment')),
                                'labor_force_participation': to_float_or_none(row.get('labor_force_participation')),
                                'average_wage': to_float_or_none(row.get('average_wage')),
                                'job_creation_rate': to_float_or_none(row.get('job_creation_rate')),
                            }
                        )
                        count += 1
                        # if created:
                        #     self.stdout.write(self.style.SUCCESS(f"Created labor market data for {governorate.name} - {year}"))
                        # else:
                        #     self.stdout.write(f"Updated labor market data for {governorate.name} - {year}")
                    except TunisiaGovernorate.DoesNotExist:
                        self.stderr.write(self.style.ERROR(f"Governorate '{governorate_name}' not found for labor market data. Row: {row}"))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error processing labor market row for {governorate_name} - {year}: {e} - Row: {row}"))
                self.stdout.write(self.style.SUCCESS(f"Processed {count} labor market data records."))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {labor_market_data_path}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred while populating LaborMarketData: {e}"))

        self.stdout.write(self.style.SUCCESS('Successfully completed data population process.'))
