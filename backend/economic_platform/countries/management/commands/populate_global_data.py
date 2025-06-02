import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from countries.models import Country, EconomicIndicator # Assuming direct import works

# Helper functions from the previous command, can be refactored into a common place later
def to_int_or_none(value):
    if value == '' or value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None

def to_float_or_none(value):
    if value == '' or value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None

class Command(BaseCommand):
    help = 'Populates Country and EconomicIndicator data from WHI_Inflation.csv'

    def handle(self, *args, **options):
        # settings.BASE_DIR is backend/economic_platform/
        # Project root is settings.BASE_DIR.parent.parent
        csv_file_path = settings.BASE_DIR.parent.parent / 'WHI_Inflation.csv'

        self.stdout.write(f"Starting data population from {csv_file_path}...")

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                countries_processed = 0
                indicators_processed = 0

                for row in reader:
                    try:
                        country_name = row.get('Country')
                        year_str = row.get('Year')
                        
                        if not country_name or not year_str:
                            self.stderr.write(self.style.WARNING(f"Skipping row due to missing Country or Year: {row}"))
                            continue
                        
                        year = to_int_or_none(year_str)
                        if year is None:
                            self.stderr.write(self.style.WARNING(f"Skipping row due to invalid Year for {country_name}: {year_str}"))
                            continue

                        # Country.objects.update_or_create for Country model
                        # ISO Code is missing from CSV, so 'code' will be blank for new entries or rely on existing
                        # Latitude and Longitude are missing, will be blank
                        try:
                            country = Country.objects.get(name=country_name)
                            country_created = False
                            # Optionally update continent if it's different and provided in CSV
                            new_continent = row.get('Continent/Region')
                            if new_continent and country.continent != new_continent:
                                country.continent = new_continent
                                country.save(update_fields=['continent'])
                                # self.stdout.write(f"Updated continent for {country.name}")
                        except Country.DoesNotExist:
                            self.stderr.write(self.style.WARNING(f"Country '{country_name}' not found. Skipping its economic indicators as it cannot be created without a unique ISO code from CSV."))
                            continue # Skip to next row

                        # EconomicIndicator.objects.update_or_create
                        indicator_defaults = {
                            'headline_consumer_price_inflation': to_float_or_none(row.get('Headline Consumer Price Inflation')),
                            'energy_consumer_price_inflation': to_float_or_none(row.get('Energy Consumer Price Inflation')),
                            'food_consumer_price_inflation': to_float_or_none(row.get('Food Consumer Price Inflation')),
                            'official_core_consumer_price_inflation': to_float_or_none(row.get('Official Core Consumer Price Inflation')),
                            'producer_price_inflation': to_float_or_none(row.get('Producer Price Inflation')),
                            'gdp_deflator_index_growth_rate': to_float_or_none(row.get('GDP deflator Index growth rate')),
                            'happiness_score': to_float_or_none(row.get('Score')),
                            'gdp_per_capita': to_float_or_none(row.get('GDP per Capita')),
                            'social_support': to_float_or_none(row.get('Social support')),
                            'healthy_life_expectancy_at_birth': to_float_or_none(row.get('Healthy life expectancy at birth')),
                            'freedom_to_make_life_choices': to_float_or_none(row.get('Freedom to make life choices')),
                            'generosity': to_float_or_none(row.get('Generosity')),
                            'perceptions_of_corruption': to_float_or_none(row.get('Perceptions of corruption')),
                        }
                        
                        indicator, indicator_created = EconomicIndicator.objects.update_or_create(
                            country=country,
                            year=year,
                            defaults=indicator_defaults
                        )
                        
                        if country_created: # This will now always be false with the new logic
                            countries_processed += 1 
                        if indicator_created:
                            indicators_processed += 1
                        
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error processing indicator for {country_name} - {year}: {e} - Row: {row}"))
                
                self.stdout.write(self.style.SUCCESS(f"Countries processed (updated existing): {Country.objects.count()} total in DB. New countries created in this run: {countries_processed} (should be 0)."))
                self.stdout.write(self.style.SUCCESS(f"Economic indicators processed. New indicators created: {indicators_processed}. Existing were updated."))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {csv_file_path}"))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
            return

        self.stdout.write(self.style.SUCCESS('Successfully completed global data population.'))
