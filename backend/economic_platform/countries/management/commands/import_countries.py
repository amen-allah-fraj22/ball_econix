import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
# Assuming 'backend.economic_platform.countries' is a valid app recognized by Django
# and 'models' is where Country model is defined.
# If 'countries' is the app name itself and is in INSTALLED_APPS:
# from countries.models import Country
# Or if 'economic_platform' is an app and countries is a model file (less likely):
# from economic_platform.models import Country
# For now, using the path provided in the problem description:
from backend.economic_platform.countries.models import Country

class Command(BaseCommand):
    help = 'Imports countries from WHI_Inflation.csv into the Country model'

    def handle(self, *args, **options):
        # Construct the full path to the CSV file
        # Assuming BASE_DIR is defined in settings.py and points to the project's root directory
        # where WHI_Inflation.csv is located.
        file_path = os.path.join(settings.BASE_DIR, 'WHI_Inflation.csv')
        
        self.stdout.write(self.style.NOTICE(f"Attempting to import countries from: {file_path}"))

        try:
            with open(file_path, mode='r', encoding='utf-8-sig') as file: # Using utf-8-sig to handle potential BOM
                reader = csv.DictReader(file)
                
                # Verify that 'Country' column exists
                if 'Country' not in reader.fieldnames:
                    self.stderr.write(self.style.ERROR("CSV file must contain a 'Country' column. Please check the header."))
                    self.stderr.write(self.style.ERROR(f"Found columns: {reader.fieldnames}"))
                    return

                countries_added = 0
                countries_existing = 0
                rows_processed = 0
                
                for row_number, row in enumerate(reader, 1): # Start row_number from 1 for user feedback
                    rows_processed += 1
                    country_name = row.get('Country', '').strip() # Use .get for safety and strip whitespace
                    
                    if not country_name:
                        self.stdout.write(self.style.WARNING(f"Row {row_number}: Skipping row due to empty country name."))
                        continue

                    # Using get_or_create to avoid duplicates
                    # It returns a tuple: (object, created_boolean)
                    country_obj, created = Country.objects.get_or_create(
                        name=country_name
                        # If you have a 'code' field in your Country model and CSV:
                        # defaults={'code': row.get('Country Code', '').strip()} # Example: get code too
                    )
                    
                    if created:
                        countries_added += 1
                        # self.stdout.write(self.style.SUCCESS(f"Row {row_number}: Added new country: {country_name}"))
                    else:
                        countries_existing += 1
                        # self.stdout.write(f"Row {row_number}: Country already exists: {country_name}")

                self.stdout.write(self.style.SUCCESS(f"\nFinished importing countries."))
                self.stdout.write(f"Total rows processed (excluding header): {rows_processed}")
                self.stdout.write(f"New countries added: {countries_added}")
                self.stdout.write(f"Countries that already existed: {countries_existing}")

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Error: The file {file_path} was not found."))
            self.stderr.write(self.style.ERROR("Please ensure 'WHI_Inflation.csv' is in the project root directory."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An unexpected error occurred: {e}"))
            self.stderr.write(self.style.ERROR("Check CSV format, encoding, and database connectivity."))
