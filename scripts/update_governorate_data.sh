#!/bin/bash

# Navigate to the project root directory
cd "$(dirname "$0")/.."

# Activate virtual environment (adjust path as needed)
source venv/Scripts/activate

# Run Django migrations (optional, but recommended)
python backend/economic_platform/manage.py makemigrations governorates
python backend/economic_platform/manage.py migrate

# Run the update script
python scripts/update_governorate_data.py

# Deactivate virtual environment
deactivate 