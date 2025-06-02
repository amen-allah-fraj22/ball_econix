import csv
from django.core.management.base import BaseCommand
from tunisia.models import TunisiaGovernorate, RealEstatePrices
from django.db import IntegrityError
import logging

# Configure logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Populates the RealEstatePrices model from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file containing real estate data.')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        self.stdout.write(self.style.SUCCESS(f'Starting to populate real estate prices from {csv_file_path}'))

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        governorate_name = row.get('governorate')
                        year = row.get('year')

                        if not governorate_name or not year:
                            logger.warning(f"Skipping row due to missing governorate or year: {row}")
                            continue

                        try:
                            governorate = TunisiaGovernorate.objects.get(name=governorate_name)
                        except TunisiaGovernorate.DoesNotExist:
                            logger.error(f"Governorate '{governorate_name}' not found. Skipping row: {row}")
                            continue

                        year = int(year)

                        # Avoid creating duplicate entries
                        obj, created = RealEstatePrices.objects.get_or_create(
                            governorate=governorate,
                            year=year,
                            defaults={
                                'residential_price_per_m2': float(row['residential_price_per_m2']) if row.get('residential_price_per_m2') else None,
                                'commercial_price_per_m2': float(row['commercial_price_per_m2']) if row.get('commercial_price_per_m2') else None,
                                'land_price_per_m2': float(row['land_price_per_m2']) if row.get('land_price_per_m2') else None,
                            }
                        )

                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Successfully created real estate price entry for {governorate_name} - {year}'))
                        else:
                            self.stdout.write(self.style.NOTICE(f'Real estate price entry for {governorate_name} - {year} already exists. Skipping creation.'))

                    except ValueError as e:
                        logger.error(f"Skipping row due to data conversion error: {row} - {e}")
                    except IntegrityError as e:
                        logger.error(f"Skipping row due to integrity error: {row} - {e}")
                    except Exception as e:
                        logger.error(f"An unexpected error occurred while processing row {row}: {e}")

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'Error: CSV file not found at {csv_file_path}'))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An unexpected error occurred: {e}'))
            return

        self.stdout.write(self.style.SUCCESS('Finished populating real estate prices.'))
