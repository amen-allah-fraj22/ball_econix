import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from countries.models import Country, EconomicIndicator # Assuming these are the final model names
from django.conf import settings # To construct file path
import os
import numpy as np # For mean calculation

# Define expected CSV columns based on the model (after refinement)
# These are the names as they appear in the CSV file.
CSV_COLUMN_MAPPING = {
    'Country': 'country_name', # Special handling: used to find/create Country object
    'Year': 'year',
    'Headline Consumer Price Inflation': 'headline_consumer_price_inflation',
    'Energy Consumer Price Inflation': 'energy_consumer_price_inflation',
    'Food Consumer Price Inflation': 'food_consumer_price_inflation',
    'Official Core Consumer Price Inflation': 'official_core_consumer_price_inflation',
    'Producer Price Inflation': 'producer_price_inflation',
    'GDP Deflator Index Growth Rate': 'gdp_deflator_index_growth_rate',
    'Score': 'happiness_score',
    'GDP per Capita': 'gdp_per_capita',
    'Social Support': 'social_support',
    'Healthy Life Expectancy at Birth': 'healthy_life_expectancy_at_birth',
    'Freedom to Make Life Choices': 'freedom_to_make_life_choices',
    'Generosity': 'generosity',
    'Perceptions of Corruption': 'perceptions_of_corruption',
    # 'Continent/Region' is associated with Country model, not directly imported into EconomicIndicator here.
    # It will be used to create/update Country.continent if not already set.
    'Continent/Region': 'continent_region'
}

# Define which columns are numeric and might need cleaning/mean imputation
NUMERIC_COLUMNS = [
    'headline_consumer_price_inflation', 'energy_consumer_price_inflation',
    'food_consumer_price_inflation', 'official_core_consumer_price_inflation',
    'producer_price_inflation', 'gdp_deflator_index_growth_rate', 'happiness_score',
    'gdp_per_capita', 'social_support', 'healthy_life_expectancy_at_birth',
    'freedom_to_make_life_choices', 'generosity', 'perceptions_of_corruption'
]

class Command(BaseCommand):
    help = 'Imports economic data from WHI_Inflation.csv into the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file-path',
            type=str,
            help='Optional: The absolute path to the CSV file.',
                default=os.path.join(settings.BASE_DIR, 'data', 'WHI_Inflation.csv') # Corrected path
        )

    @transaction.atomic
    def handle(self, *args, **options):
        file_path = options['file_path']
        self.stdout.write(self.style.SUCCESS(f'Starting data import from {file_path}'))

        # Counters for logging
        rows_processed = 0
        countries_created = 0
        countries_updated = 0
        indicators_created = 0
        indicators_updated = 0
        errors = 0
        # duplicates_skipped = 0 # Or how you define duplicates, current implementation updates

        try:
            # 1. Read WHI_Inflation.csv using pandas
            df = pd.read_csv(file_path)
            rows_processed = len(df)
            self.stdout.write(self.style.SUCCESS(f'Successfully read {rows_processed} rows from CSV.'))

            # Rename columns to match model fields for easier processing
            df_renamed = df.rename(columns=CSV_COLUMN_MAPPING)

            # 2. Clean and validate data
            # Handle missing values with column means for specified numeric columns
            for col_model_name in NUMERIC_COLUMNS:
                if col_model_name in df_renamed.columns:
                    # Convert column to numeric, coercing errors to NaN
                    df_renamed[col_model_name] = pd.to_numeric(df_renamed[col_model_name], errors='coerce')
                    if df_renamed[col_model_name].isnull().any():
                        mean_val = df_renamed[col_model_name].mean()
                        df_renamed[col_model_name].fillna(mean_val, inplace=True)
                        self.stdout.write(f"Filled NaN in '{col_model_name}' with mean: {mean_val:.2f}")
                else:
                    self.stdout.write(self.style.WARNING(f"Numeric column '{col_model_name}' (mapped from CSV) not found in DataFrame after renaming."))


            # Validate data ranges (simple example for inflation)
            inflation_cols = [
                'headline_consumer_price_inflation', 'energy_consumer_price_inflation',
                'food_consumer_price_inflation', 'official_core_consumer_price_inflation',
                'producer_price_inflation'
            ]
            for col in inflation_cols:
                if col in df_renamed.columns:
                    if (df_renamed[col] < -50).any() or (df_renamed[col] > 200).any():
                         self.stdout.write(self.style.WARNING(f"Warning: Column '{col}' contains values outside typical range (-50% to 200%)."))


            # 3. Create/update Country records & EconomicIndicator records
            for index, row in df_renamed.iterrows():
                try:
                    country_name = row.get('country_name')
                    year_val = row.get('year') # Keep as year_val to avoid conflict with year column name
                    continent_region = row.get('continent_region')

                    if not country_name or pd.isna(country_name):
                        self.stdout.write(self.style.ERROR(f"Skipping row {index+2} due to missing country name."))
                        errors += 1
                        continue

                    if year_val is None or pd.isna(year_val):
                        self.stdout.write(self.style.ERROR(f"Skipping row {index+2} for country {country_name} due to missing year."))
                        errors += 1
                        continue
                    year_int = int(year_val)


                    country_defaults = {}
                    if continent_region and not pd.isna(continent_region):
                        # Simple split: assumes "Continent / Region" or "Continent"
                        parts = [p.strip() for p in continent_region.split('/', 1)]
                        country_defaults['continent'] = parts[0]
                        if len(parts) > 1:
                            country_defaults['region'] = parts[1]
                        else:
                            # If no '/' is present, use the whole string for continent and leave region blank or as per model default
                            country_defaults['region'] = '' # Or handle as needed by Country model (e.g. allow blank)


                    country, created = Country.objects.update_or_create(
                        name=country_name,
                        defaults=country_defaults
                    )
                    if created:
                        countries_created += 1
                        # self.stdout.write(f"Created new country: {country_name}") # Less verbose
                    else:
                        updated_fields = False
                        for key, value in country_defaults.items():
                            if getattr(country, key) != value:
                                setattr(country, key, value)
                                updated_fields = True
                        if updated_fields:
                            country.save()
                            countries_updated +=1
                            # self.stdout.write(f"Updated existing country: {country_name}") # Less verbose


                    # Prepare data for EconomicIndicator
                    indicator_data = {} # Changed from {'country': country, 'year': year_int} to build dynamically
                    for csv_col_header, model_field_name in CSV_COLUMN_MAPPING.items():
                        # model_field_name is the key in df_renamed (already mapped)
                        # We need to check if this model_field_name is one of the target fields for EconomicIndicator
                        # (i.e., it's in NUMERIC_COLUMNS or other specific fields like 'year')
                        if model_field_name in NUMERIC_COLUMNS: # Check against the list of numeric fields for the indicator
                            if model_field_name in row and not pd.isna(row[model_field_name]):
                                indicator_data[model_field_name] = row[model_field_name]

                    # Create or update EconomicIndicator
                    indicator, ei_created = EconomicIndicator.objects.update_or_create(
                        country=country,
                        year=year_int,
                        defaults=indicator_data
                    )
                    if ei_created:
                        indicators_created += 1
                    else:
                        indicators_updated += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing row {index+2} for country '{row.get('country_name')}': {e}"))
                    errors += 1
                    continue

            self.stdout.write(self.style.SUCCESS('Data import process completed.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Error: The file {file_path} was not found."))
            self.stdout.write(self.style.WARNING(f"Please ensure WHI_Inflation.csv is in 'backend/economic_platform/data/', or specify the correct path with --file-path."))
            errors +=1
        except pd.errors.EmptyDataError:
            self.stdout.write(self.style.ERROR(f"Error: The file {file_path} is empty or not valid CSV."))
            errors +=1
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An unexpected error occurred: {e}"))
            self.stdout.write(self.style.ERROR(f"Error type: {type(e).__name__}"))
            import traceback
            self.stdout.write(self.style.ERROR(f"Traceback: {traceback.format_exc()}"))
            errors +=1
        finally:
            self.stdout.write("--- Import Statistics ---")
            self.stdout.write(f"Total rows in CSV read: {rows_processed}")
            self.stdout.write(f"Countries created: {countries_created}")
            self.stdout.write(f"Countries updated: {countries_updated}")
            self.stdout.write(f"Economic Indicators created: {indicators_created}")
            self.stdout.write(f"Economic Indicators updated (or found existing): {indicators_updated}")
            self.stdout.write(f"Rows with errors/skipped: {errors}")
            self.stdout.write("-------------------------")
