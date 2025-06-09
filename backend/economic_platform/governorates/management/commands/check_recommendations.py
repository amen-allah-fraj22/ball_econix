from django.core.management.base import BaseCommand
from governorates.models import Governorate, Sector, RecommendationDetails

class Command(BaseCommand):
    help = 'Checks the number of investment recommendations for the Manufacturing sector and industrial zones data.'

    def handle(self, *args, **options):
        self.stdout.write('Checking for Manufacturing sector recommendations and industrial zones data...')
        try:
            manufacturing_sector = Sector.objects.get(name='Manufacturing')
            recommendations_count = RecommendationDetails.objects.filter(sector=manufacturing_sector).count()
            self.stdout.write(self.style.SUCCESS(f'Number of manufacturing recommendations: {recommendations_count}'))

            self.stdout.write('\nIndustrial Zones per Governorate:')
            governorates = Governorate.objects.all().order_by('name')
            for governorate in governorates:
                self.stdout.write(f'- {governorate.name}: Industrial Zones = {governorate.industrial_zones}')

        except Sector.DoesNotExist:
            self.stdout.write(self.style.ERROR('Manufacturing sector not found in the database.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}')) 