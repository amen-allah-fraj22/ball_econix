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
    'Country Code': 'code',
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
                default=r'C:\Users\amen allah fraj\Documents\GitHub\ball_econix\WHI_Inflation.csv' # Corrected absolute path with raw string
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

                    # Add country code from CSV to defaults if available
                    country_code = row.get('code') # 'code' is the mapped name from CSV_COLUMN_MAPPING
                    if country_code and not pd.isna(country_code):
                        country_defaults['code'] = country_code

                    # In a real application, you would use a geocoding service or a more comprehensive dataset.
                    COUNTRY_COORDINATES = {
                        'United States': {'latitude': 37.0902, 'longitude': -95.7129},
                        'Canada': {'latitude': 56.1304, 'longitude': -106.3468},
                        'Mexico': {'latitude': 23.6345, 'longitude': -102.5528},
                        'Brazil': {'latitude': -14.2350, 'longitude': -51.9253},
                        'Argentina': {'latitude': -34.6037, 'longitude': -58.3816},
                        'United Kingdom': {'latitude': 55.3781, 'longitude': -3.4360},
                        'France': {'latitude': 46.2276, 'longitude': 2.2137},
                        'Germany': {'latitude': 51.1657, 'longitude': 10.4515},
                        'Italy': {'latitude': 41.8719, 'longitude': 12.5674},
                        'Spain': {'latitude': 40.4637, 'longitude': -3.7492},
                        'China': {'latitude': 35.8617, 'longitude': 104.1954},
                        'India': {'latitude': 20.5937, 'longitude': 78.9629},
                        'Australia': {'latitude': -25.2744, 'longitude': 133.7751},
                        'Japan': {'latitude': 36.2048, 'longitude': 138.2529},
                        'South Africa': {'latitude': -30.5595, 'longitude': 22.9375},
                        'Egypt': {'latitude': 26.8206, 'longitude': 30.8025},
                        'Tunisia': {'latitude': 34.0, 'longitude': 9.0},
                        'Nigeria': {'latitude': 9.0820, 'longitude': 8.6753},
                        'Kenya': {'latitude': -1.286389, 'longitude': 36.817223},
                        'Russia': {'latitude': 61.5240, 'longitude': 105.3188},
                        'Saudi Arabia': {'latitude': 23.8859, 'longitude': 45.0792},
                        'United Arab Emirates': {'latitude': 23.4241, 'longitude': 53.8478},
                        'Indonesia': {'latitude': -0.7893, 'longitude': 113.9213},
                        'Pakistan': {'latitude': 30.3753, 'longitude': 69.3451},
                        'Bangladesh': {'latitude': 23.6850, 'longitude': 90.3563},
                        'Vietnam': {'latitude': 14.0583, 'longitude': 108.2772},
                        'Philippines': {'latitude': 12.8797, 'longitude': 121.7740},
                        'Turkey': {'latitude': 38.9637, 'longitude': 35.2433},
                        'Iran': {'latitude': 32.4279, 'longitude': 53.6880},
                        'Thailand': {'latitude': 15.8700, 'longitude': 100.9925},
                        'Malaysia': {'latitude': 4.2105, 'longitude': 101.9758},
                        'Poland': {'latitude': 51.9194, 'longitude': 19.1451},
                        'Ukraine': {'latitude': 48.3794, 'longitude': 31.1656},
                        'Peru': {'latitude': -9.1900, 'longitude': -75.0152},
                        'Colombia': {'latitude': 4.5709, 'longitude': -74.2973},
                        'Venezuela': {'latitude': 6.4238, 'longitude': -66.5897},
                        'Chile': {'latitude': -35.6751, 'longitude': -71.5430},
                        'Egypt': {'latitude': 26.8206, 'longitude': 30.8025},
                        'Algeria': {'latitude': 28.0339, 'longitude': 1.6596},
                        'Morocco': {'latitude': 31.7917, 'longitude': -7.0926},
                        'Greece': {'latitude': 39.0742, 'longitude': 21.8243},
                        'Portugal': {'latitude': 39.3999, 'longitude': -8.2245},
                        'Netherlands': {'latitude': 52.1326, 'longitude': 5.2913},
                        'Belgium': {'latitude': 50.8503, 'longitude': 4.3517},
                        'Sweden': {'latitude': 60.1282, 'longitude': 18.6435},
                        'Norway': {'latitude': 60.4720, 'longitude': 8.4689},
                        'Denmark': {'latitude': 56.2639, 'longitude': 9.5018},
                        'Finland': {'latitude': 61.9241, 'longitude': 25.7482},
                        'Austria': {'latitude': 47.5162, 'longitude': 14.5501},
                        'Switzerland': {'latitude': 46.8182, 'longitude': 8.2275},
                        'Ireland': {'latitude': 53.4129, 'longitude': -8.2439},
                        'New Zealand': {'latitude': -40.9006, 'longitude': 174.8860},
                        'South Korea': {'latitude': 35.9078, 'longitude': 127.7669},
                        'North Korea': {'latitude': 40.3399, 'longitude': 127.5101},
                        'Afghanistan': {'latitude': 33.9391, 'longitude': 67.7099},
                        'Albania': {'latitude': 41.1533, 'longitude': 20.1683},
                        'Angola': {'latitude': -11.2027, 'longitude': 17.8739},
                        'Armenia': {'latitude': 40.0691, 'longitude': 45.0382},
                        'Austria': {'latitude': 47.5162, 'longitude': 14.5501},
                        'Azerbaijan': {'latitude': 40.1431, 'longitude': 47.5769},
                        'Bahrain': {'latitude': 25.9304, 'longitude': 50.6378},
                        'Belarus': {'latitude': 53.7098, 'longitude': 27.9534},
                        'Belgium': {'latitude': 50.8503, 'longitude': 4.3517},
                        'Benin': {'latitude': 9.3077, 'longitude': 2.3158},
                        'Bhutan': {'latitude': 27.5142, 'longitude': 90.4336},
                        'Bolivia': {'latitude': -16.2902, 'longitude': -63.5887},
                        'Bosnia and Herzegovina': {'latitude': 43.9159, 'longitude': 17.6791},
                        'Botswana': {'latitude': -22.3285, 'longitude': 24.6849},
                        'Bulgaria': {'latitude': 42.7339, 'longitude': 25.4858},
                        'Burkina Faso': {'latitude': 12.2383, 'longitude': -1.8641},
                        'Burundi': {'latitude': -3.3733, 'longitude': 29.9189},
                        'Cambodia': {'latitude': 12.5657, 'longitude': 104.9910},
                        'Cameroon': {'latitude': 7.3697, 'longitude': 12.3547},
                        'Central African Republic': {'latitude': 6.6111, 'longitude': 20.9394},
                        'Chad': {'latitude': 15.4542, 'longitude': 18.7322},
                        'Colombia': {'latitude': 4.5709, 'longitude': -74.2973},
                        'Comoros': {'latitude': -11.6455, 'longitude': 43.3333},
                        'Congo (Brazzaville)': {'latitude': -0.2280, 'longitude': 15.8277},
                        'Congo (Kinshasa)': {'latitude': -4.0383, 'longitude': 21.7587},
                        'Costa Rica': {'latitude': 9.7489, 'longitude': -83.7534},
                        'Croatia': {'latitude': 45.1000, 'longitude': 15.2000},
                        'Cuba': {'latitude': 21.5218, 'longitude': -77.7812},
                        'Cyprus': {'latitude': 35.1264, 'longitude': 33.4299},
                        'Czech Republic': {'latitude': 49.8175, 'longitude': 15.4730},
                        'Denmark': {'latitude': 56.2639, 'longitude': 9.5018},
                        'Djibouti': {'latitude': 11.8251, 'longitude': 42.5903},
                        'Dominican Republic': {'latitude': 18.7357, 'longitude': -70.1627},
                        'Ecuador': {'latitude': -1.8312, 'longitude': -78.1834},
                        'El Salvador': {'latitude': 13.7942, 'longitude': -88.8965},
                        'Equatorial Guinea': {'latitude': 1.6596, 'longitude': 10.2679},
                        'Eritrea': {'latitude': 15.1794, 'longitude': 39.7823},
                        'Estonia': {'latitude': 58.5953, 'longitude': 25.0136},
                        'Eswatini': {'latitude': -26.5225, 'longitude': 31.4659},
                        'Ethiopia': {'latitude': 9.1450, 'longitude': 40.4897},
                        'Fiji': {'latitude': -17.7134, 'longitude': 178.0650},
                        'Finland': {'latitude': 61.9241, 'longitude': 25.7482},
                        'Gabon': {'latitude': -0.8037, 'longitude': 11.6094},
                        'Gambia': {'latitude': 13.4432, 'longitude': -15.3101},
                        'Georgia': {'latitude': 42.3154, 'longitude': 43.3569},
                        'Ghana': {'latitude': 7.9465, 'longitude': -1.0232},
                        'Greece': {'latitude': 39.0742, 'longitude': 21.8243},
                        'Guatemala': {'latitude': 15.7835, 'longitude': -90.2308},
                        'Guinea': {'latitude': 9.9456, 'longitude': -9.6966},
                        'Guinea-Bissau': {'latitude': 11.8037, 'longitude': -15.1804},
                        'Guyana': {'latitude': 4.8604, 'longitude': -58.9302},
                        'Haiti': {'latitude': 18.9712, 'longitude': -72.2852},
                        'Honduras': {'latitude': 15.199999, 'longitude': -86.241905},
                        'Hungary': {'latitude': 47.1625, 'longitude': 19.5033},
                        'Iceland': {'latitude': 64.9631, 'longitude': -19.0208},
                        'Ireland': {'latitude': 53.4129, 'longitude': -8.2439},
                        'Israel': {'latitude': 31.0461, 'longitude': 34.8516},
                        'Jamaica': {'latitude': 18.1096, 'longitude': -77.2975},
                        'Jordan': {'latitude': 30.5852, 'longitude': 36.2384},
                        'Kazakhstan': {'latitude': 48.0196, 'longitude': 66.9237},
                        'Kuwait': {'latitude': 29.3117, 'longitude': 47.4818},
                        'Kyrgyzstan': {'latitude': 41.2044, 'longitude': 74.7661},
                        'Laos': {'latitude': 19.8563, 'longitude': 102.4955},
                        'Latvia': {'latitude': 56.8796, 'longitude': 24.6032},
                        'Lebanon': {'latitude': 33.8547, 'longitude': 35.8623},
                        'Lesotho': {'latitude': -29.6099, 'longitude': 28.2336},
                        'Liberia': {'latitude': 6.4281, 'longitude': -9.4295},
                        'Libya': {'latitude': 26.3351, 'longitude': 17.2283},
                        'Lithuania': {'latitude': 55.1694, 'longitude': 23.8813},
                        'Luxembourg': {'latitude': 49.8153, 'longitude': 6.1296},
                        'Madagascar': {'latitude': -18.7669, 'longitude': 46.8691},
                        'Malawi': {'latitude': -13.2543, 'longitude': 34.3015},
                        'Maldives': {'latitude': 3.2028, 'longitude': 73.2207},
                        'Mali': {'latitude': 17.5707, 'longitude': -3.9962},
                        'Malta': {'latitude': 35.9375, 'longitude': 14.3754},
                        'Mauritania': {'latitude': 21.0079, 'longitude': -10.9408},
                        'Mauritius': {'latitude': -20.3484, 'longitude': 57.5522},
                        'Moldova': {'latitude': 47.4116, 'longitude': 28.3699},
                        'Mongolia': {'latitude': 46.8625, 'longitude': 103.8467},
                        'Montenegro': {'latitude': 42.7087, 'longitude': 19.3744},
                        'Mozambique': {'latitude': -18.6657, 'longitude': 35.5296},
                        'Myanmar': {'latitude': 21.9139, 'longitude': 95.9562},
                        'Namibia': {'latitude': -22.9576, 'longitude': 18.4904},
                        'Nepal': {'latitude': 28.3949, 'longitude': 84.1240},
                        'Nicaragua': {'latitude': 12.8654, 'longitude': -85.2072},
                        'Niger': {'latitude': 17.6078, 'longitude': 8.0817},
                        'North Macedonia': {'latitude': 41.6086, 'longitude': 21.7453},
                        'Oman': {'latitude': 21.5125, 'longitude': 55.9232},
                        'Panama': {'latitude': 8.5380, 'longitude': -80.7821},
                        'Paraguay': {'latitude': -23.4425, 'longitude': -58.4438},
                        'Peru': {'latitude': -9.1900, 'longitude': -75.0152},
                        'Qatar': {'latitude': 25.3548, 'longitude': 51.1839},
                        'Romania': {'latitude': 45.9432, 'longitude': 24.9668},
                        'Rwanda': {'latitude': -1.9403, 'longitude': 29.8739},
                        'San Marino': {'latitude': 43.9424, 'longitude': 12.4578},
                        'Senegal': {'latitude': 14.4974, 'longitude': -14.4524},
                        'Serbia': {'latitude': 44.0165, 'longitude': 21.0059},
                        'Sierra Leone': {'latitude': 8.4606, 'longitude': -11.7799},
                        'Singapore': {'latitude': 1.3521, 'longitude': 103.8198},
                        'Slovakia': {'latitude': 48.6690, 'longitude': 19.6990},
                        'Slovenia': {'latitude': 46.1512, 'longitude': 14.9955},
                        'Somalia': {'latitude': 0.0000, 'longitude': 45.0000},
                        'South Sudan': {'latitude': 6.8770, 'longitude': 31.3070},
                        'Sri Lanka': {'latitude': 7.8731, 'longitude': 80.7718},
                        'Sudan': {'latitude': 12.8628, 'longitude': 30.2176},
                        'Syria': {'latitude': 34.8021, 'longitude': 38.9968},
                        'Tanzania': {'latitude': -6.3690, 'longitude': 34.8888},
                        'Timor-Leste': {'latitude': -8.8742, 'longitude': 125.7275},
                        'Togo': {'latitude': 8.6195, 'longitude': 1.1655},
                        'Trinidad and Tobago': {'latitude': 10.6918, 'longitude': -61.2225},
                        'Uganda': {'latitude': 1.3733, 'longitude': 32.2903},
                        'Uruguay': {'latitude': -32.5228, 'longitude': -55.7658},
                        'Uzbekistan': {'latitude': 41.3775, 'longitude': 64.5853},
                        'Yemen': {'latitude': 15.5527, 'longitude': 48.5164},
                        'Zambia': {'latitude': -13.1339, 'longitude': 27.8493},
                        'Zimbabwe': {'latitude': -19.0154, 'longitude': 29.1549},
                    }

                    if country_name in COUNTRY_COORDINATES:
                        coords = COUNTRY_COORDINATES[country_name]
                        country_defaults['latitude'] = coords['latitude']
                        country_defaults['longitude'] = coords['longitude']


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
