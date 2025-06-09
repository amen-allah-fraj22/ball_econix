import csv
from django.core.management.base import BaseCommand
from governorates.models import Governorate, LaborMarketData, RealEstateData, Sector, RecommendationDetails

class Command(BaseCommand):
    help = 'Loads sample sector and recommendation details data.'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample sectors...')
        self.load_sectors()
        self.stdout.write('Sample sectors loaded.')

        self.stdout.write('Ensuring governorate data is prepared...')
        self.ensure_governorate_data()
        self.stdout.write('Governorate data prepared.')

        self.stdout.write('Loading sample recommendation details...')
        # Clear existing recommendation details to ensure fresh data generation
        RecommendationDetails.objects.all().delete()
        self.load_recommendation_details()
        self.stdout.write('Sample recommendation details loaded.')

        self.stdout.write(self.style.SUCCESS('Successfully loaded sample data.'))

    def load_sectors(self):
        sectors = [
            {'name': 'Tourism', 'description': 'Focus on hotel, resort, and tourism-related services.'},
            {'name': 'Agriculture', 'description': 'Investment in farming, crop production, and livestock.'},
            {'name': 'Technology', 'description': 'Opportunities in IT, software development, and tech startups.'},
            {'name': 'Manufacturing', 'description': 'Industrial production and assembly plants.'},
            {'name': 'Renewable Energy', 'description': 'Projects in solar, wind, and other clean energy sources.'},
        ]

        for sector_data in sectors:
            Sector.objects.get_or_create(name=sector_data['name'], defaults={'description': sector_data['description']})

    def ensure_governorate_data(self):
        """Ensures that necessary governorate data (like industrial_zones) is set for recommendations."""
        for governorate in Governorate.objects.all():
            if governorate.industrial_zones == 0:
                governorate.industrial_zones = 1  # Set to a positive value to enable manufacturing recommendations
                governorate.save()
            # Add similar logic for other fields if necessary for other sectors

    def load_recommendation_details(self):
        governorates = Governorate.objects.all()
        sectors = Sector.objects.all()

        for governorate in governorates:
            # Example: Generate recommendations for Tourism in coastal areas
            if governorate.coastal_access and Sector.objects.filter(name='Tourism').exists():
                tourism_sector = Sector.objects.get(name='Tourism')
                RecommendationDetails.objects.get_or_create(
                    governorate=governorate,
                    sector=tourism_sector,
                    defaults={
                        'ranking_score': 75 + (governorate.tourist_attractions * 2) if governorate.tourist_attractions else 75, # Example score
                        'contact_info_investment_offices': f'Contact the local tourism investment office in {governorate.name}. Phone: +216-XX-XXXXXX',
                        'relevant_government_agencies': 'Ministry of Tourism, FIPA Tunisia',
                        'required_permits_procedures': 'Tourism license, environmental permits, building permits.',
                        'timeline_for_setup': '6-12 months',
                        'investment_size_recommendations': 'Medium to Large scale (e.g., $1M - $10M+)',
                        'infrastructure_details': f'Well-developed road network, proximity to {governorate.name} airport. Good internet connectivity in tourist zones.',
                        'economic_incentives': 'Tax exemptions for tourism projects, access to tourism development funds.',
                        'geographic_advantages': f'Beautiful beaches and historical sites, favorable climate for tourism in {governorate.name}.',
                        'cost_analysis_summary': 'Competitive land prices for tourism development, average utility costs.',
                        'success_stories': 'Several successful hotel chains and resorts operate here.',
                    }
                )

            # Example: Generate recommendations for Agriculture in areas with high agricultural land percent
            if governorate.agricultural_land_percent > 30 and Sector.objects.filter(name='Agriculture').exists():
                agriculture_sector = Sector.objects.get(name='Agriculture')
                RecommendationDetails.objects.get_or_create(
                    governorate=governorate,
                    sector=agriculture_sector,
                    defaults={
                        'ranking_score': 80 + int(governorate.agricultural_land_percent / 5), # Example score
                        'contact_info_investment_offices': f'Contact the Ministry of Agriculture regional office in {governorate.name}. Email: info.agri@{governorate.name.lower()}.gov.tn',
                        'relevant_government_agencies': 'Ministry of Agriculture, APIA (Agency for the Promotion of Agricultural Investment)',
                        'required_permits_procedures': 'Agricultural exploitation permits, water rights.',
                        'timeline_for_setup': '3-9 months',
                        'investment_size_recommendations': 'Small to Medium scale (e.g., $100K - $5M)',
                        'infrastructure_details': 'Good rural road access, irrigation systems available.',
                        'economic_incentives': 'Subsidies for agricultural equipment, tax breaks for new farms.',
                        'geographic_advantages': f'Fertile lands and diverse climate suitable for various crops in {governorate.name}.',
                        'cost_analysis_summary': 'Affordable land prices, moderate utility costs.',
                        'success_stories': 'Flourishing olive groves and citrus farms.',
                    }
                )

            # Example: Generate recommendations for Manufacturing in industrial zones
            if governorate.industrial_zones > 0 and Sector.objects.filter(name='Manufacturing').exists():
                manufacturing_sector = Sector.objects.get(name='Manufacturing')
                RecommendationDetails.objects.get_or_create(
                    governorate=governorate,
                    sector=manufacturing_sector,
                    defaults={
                        'ranking_score': 70 + (governorate.industrial_zones * 3), # Example score
                        'contact_info_investment_offices': f'Contact the industrial development agency in {governorate.name}. Web: www.industrial-{governorate.name.lower()}.tn',
                        'relevant_government_agencies': 'Ministry of Industry, API (Agency for the Promotion of Industry and Innovation)',
                        'required_permits_procedures': 'Industrial operating license, environmental compliance.',
                        'timeline_for_setup': '8-15 months',
                        'investment_size_recommendations': 'Medium to Large scale (e.g., $5M - $50M+)',
                        'infrastructure_details': f'Proximity to major highways and ports, reliable electricity and water supply in {governorate.name} industrial zones.',
                        'economic_incentives': 'Grants for job creation, reduced taxes for export-oriented manufacturing.',
                        'geographic_advantages': 'Strategic location for logistics and distribution.',
                        'cost_analysis_summary': 'Competitive labor costs, access to industrial land.',
                        'success_stories': 'Leading textile and automotive component factories.',
                    }
                )

            # Example: Generate recommendations for Technology in high population density areas
            if governorate.population_density > 1000 and Sector.objects.filter(name='Technology').exists():
                technology_sector = Sector.objects.get(name='Technology')
                RecommendationDetails.objects.get_or_create(
                    governorate=governorate,
                    sector=technology_sector,
                    defaults={
                        'ranking_score': 85 + int(governorate.population_density / 200), # Example score
                        'contact_info_investment_offices': f'Contact the tech hub in {governorate.name}. Email: tech@{governorate.name.lower()}.com',
                        'relevant_government_agencies': 'Ministry of Communication Technologies, Smart Tunisia Initiative',
                        'required_permits_procedures': 'Business registration, innovation permits.',
                        'timeline_for_setup': '2-6 months',
                        'investment_size_recommendations': 'Small to Medium scale (e.g., $50K - $2M)',
                        'infrastructure_details': 'High-speed internet infrastructure, co-working spaces available.',
                        'economic_incentives': 'Startup grants, tax credits for R&D.',
                        'geographic_advantages': 'Access to skilled workforce and universities.',
                        'cost_analysis_summary': 'Reasonable office rental costs, competitive salaries for tech talent.',
                        'success_stories': 'Vibrant startup ecosystem, successful software development firms.',
                    }
                )

            # Example: Generate recommendations for Renewable Energy in areas with high area_km2 (assuming space for solar/wind)
            if governorate.area_km2 > 2000 and Sector.objects.filter(name='Renewable Energy').exists():
                renewable_energy_sector = Sector.objects.get(name='Renewable Energy')
                RecommendationDetails.objects.get_or_create(
                    governorate=governorate,
                    sector=renewable_energy_sector,
                    defaults={
                        'ranking_score': 78 + int(governorate.area_km2 / 500), # Example score
                        'contact_info_investment_offices': f'Contact the National Agency for Energy Management (ANME) in {governorate.name}. ',
                        'relevant_government_agencies': 'Ministry of Energy, ANME',
                        'required_permits_procedures': 'Energy production license, land acquisition permits.',
                        'timeline_for_setup': '12-24 months',
                        'investment_size_recommendations': 'Large scale (e.g., $10M - $100M+)',
                        'infrastructure_details': 'Access to national grid, suitable land for solar/wind farms.',
                        'economic_incentives': 'Feed-in tariffs, tax breaks for renewable energy projects.',
                        'geographic_advantages': 'Abundant sunshine and wind resources.',
                        'cost_analysis_summary': 'Low land costs, significant upfront investment.',
                        'success_stories': 'Several large-scale solar and wind farms in operation.',
                    }
                ) 