import csv
from django.core.management.base import BaseCommand
from tunisia.models import TunisiaGovernorate
from django.db import IntegrityError
import logging

# Configure logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Populates the TunisiaGovernorate model from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file containing governorate data.')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        self.stdout.write(self.style.SUCCESS(f'Starting to populate governorates from {csv_file_path}'))

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        name = row.get('name')
                        if not name:
                            logger.warning(f"Skipping row due to missing name: {row}")
                            continue

                        # Avoid creating duplicate entries
                        governorate, created = TunisiaGovernorate.objects.get_or_create(
                            name=name,
                            defaults={
                                'arabic_name': row.get('arabic_name'),
                                'latitude': float(row['latitude']) if row.get('latitude') else None,
                                'longitude': float(row['longitude']) if row.get('longitude') else None,
                                'population_2024': int(row['population_2024']) if row.get('population_2024') else None,
                                'area_km2': float(row['area_km2']) if row.get('area_km2') else None,
                                'unemployment_rate': float(row['unemployment_rate']) if row.get('unemployment_rate') else None,
                                'agricultural_land_percent': float(row['agricultural_land_percent']) if row.get('agricultural_land_percent') else None,
                                'population_density': float(row['population_density']) if row.get('population_density') else None,
                                'labor_force_size': int(row['labor_force_size']) if row.get('labor_force_size') else None,
                                'gdp_contribution': float(row['gdp_contribution']) if row.get('gdp_contribution') else None,
                                'coastal_access': row.get('coastal_access', '0').strip() == '1', # Parse boolean
                                'industrial_zones': int(row['industrial_zones']) if row.get('industrial_zones') else None,
                                'tourist_attractions': int(row['tourist_attractions']) if row.get('tourist_attractions') else None,
                            }
                        )

                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Successfully created governorate: {name}'))
                        else:
                            # Optionally update existing records if needed, or just log
                            self.stdout.write(self.style.NOTICE(f'Governorate {name} already exists. Skipping creation.'))
                            # Example of updating:
                            # for key, value in defaults.items():
                            #     setattr(governorate, key, value)
                            # governorate.save()
                            # self.stdout.write(self.style.SUCCESS(f'Successfully updated governorate: {name}'))


                    except ValueError as e:
                        logger.error(f"Skipping row due to data conversion error: {row} - {e}")
                    except IntegrityError as e:
                        logger.error(f"Skipping row due to integrity error (possibly duplicate non-name field): {row} - {e}")
                    except Exception as e:
                        logger.error(f"An unexpected error occurred while processing row {row}: {e}")

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'Error: CSV file not found at {csv_file_path}'))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An unexpected error occurred: {e}'))
            return

        self.stdout.write(self.style.SUCCESS('Finished populating governorates.'))
