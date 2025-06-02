import csv
from django.core.management.base import BaseCommand
from tunisia.models import TunisiaGovernorate
from analytics.models import LaborMarketData
from django.db import IntegrityError
import logging

# Configure logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Populates the LaborMarketData model from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file containing labor market data.')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        self.stdout.write(self.style.SUCCESS(f'Starting to populate labor market data from {csv_file_path}'))

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        governorate_name = row.get('governorate')
                        year_str = row.get('year')

                        if not governorate_name or not year_str:
                            logger.warning(f"Skipping row due to missing governorate or year: {row}")
                            continue

                        try:
                            governorate = TunisiaGovernorate.objects.get(name=governorate_name)
                        except TunisiaGovernorate.DoesNotExist:
                            logger.error(f"Governorate '{governorate_name}' not found. Skipping row: {row}")
                            continue

                        year = int(year_str)

                        # Avoid creating duplicate entries
                        obj, created = LaborMarketData.objects.get_or_create(
                            governorate=governorate,
                            year=year,
                            defaults={
                                'unemployment_rate': float(row['unemployment_rate']) if row.get('unemployment_rate') else None,
                                'youth_unemployment': float(row['youth_unemployment']) if row.get('youth_unemployment') else None,
                                'female_unemployment': float(row['female_unemployment']) if row.get('female_unemployment') else None,
                                'labor_force_participation': float(row['labor_force_participation']) if row.get('labor_force_participation') else None,
                                'average_wage': float(row['average_wage']) if row.get('average_wage') else None,
                                'job_creation_rate': float(row['job_creation_rate']) if row.get('job_creation_rate') else None,
                            }
                        )

                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Successfully created labor market data for {governorate_name} - {year}'))
                        else:
                            self.stdout.write(self.style.NOTICE(f'Labor market data for {governorate_name} - {year} already exists. Skipping creation.'))

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

        self.stdout.write(self.style.SUCCESS('Finished populating labor market data.'))
