# Governorate Data Update Script

## Purpose
This script updates the governorate data in the database using the CSV file located at `newdata/tunisia_gov_data.csv`.

## Prerequisites
- Python 3.8+
- Django
- Pandas
- Your Django project's virtual environment activated

## Installation
1. Ensure you have the required dependencies:
```bash
pip install pandas django
```

## Usage
Run the script from the project root directory:
```bash
python scripts/update_governorate_data.py
```

## What the Script Does
- Reads the CSV file with governorate data
- Updates or creates Governorate model instances
- Populates fields including:
  - Population (2024)
  - Unemployment Rate
  - Arabic Name
  - Geographic Coordinates
  - Area
  - Labor Force Statistics
  - And more...

## Notes
- Ensure your Django project's settings are correctly configured
- The script uses `get_or_create()` to handle existing and new governorates
- Existing governorate records will be updated with the latest data 