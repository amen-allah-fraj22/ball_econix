from django.db import models

# Create your models here.

class Governorate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    arabic_name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    population_2024 = models.IntegerField()
    area_km2 = models.FloatField()
    unemployment_rate = models.FloatField()
    agricultural_land_percent = models.FloatField()
    population_density = models.FloatField()
    labor_force_size = models.IntegerField()
    gdp_contribution = models.FloatField()
    coastal_access = models.BooleanField()
    industrial_zones = models.IntegerField()
    tourist_attractions = models.IntegerField()

    def __str__(self):
        return self.name

class LaborMarketData(models.Model):
    governorate = models.ForeignKey(Governorate, on_delete=models.CASCADE, related_name='labor_data')
    year = models.IntegerField()
    unemployment_rate = models.FloatField()
    youth_unemployment = models.FloatField()
    female_unemployment = models.FloatField()
    labor_force_participation = models.FloatField()
    average_wage = models.FloatField()
    job_creation_rate = models.FloatField()

    def __str__(self):
        return f"{self.governorate.name} - {self.year} Labor Data"

    class Meta:
        unique_together = ('governorate', 'year')

class RealEstateData(models.Model):
    governorate = models.ForeignKey(Governorate, on_delete=models.CASCADE, related_name='real_estate_data')
    year = models.IntegerField()
    residential_price_per_m2 = models.FloatField()
    commercial_price_per_m2 = models.FloatField()
    land_price_per_m2 = models.FloatField()

    def __str__(self):
        return f"{self.governorate.name} - {self.year} Real Estate Data"

    class Meta:
        unique_together = ('governorate', 'year')

class Sector(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class RecommendationDetails(models.Model):
    governorate = models.ForeignKey(Governorate, on_delete=models.CASCADE, related_name='recommendations')
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name='recommendations')
    
    # Actionable Next Steps
    contact_info_investment_offices = models.TextField(blank=True, null=True)
    relevant_government_agencies = models.TextField(blank=True, null=True)
    required_permits_procedures = models.TextField(blank=True, null=True)
    timeline_for_setup = models.CharField(max_length=255, blank=True, null=True)
    investment_size_recommendations = models.TextField(blank=True, null=True)

    # Comprehensive Data Display
    ranking_score = models.IntegerField(blank=True, null=True)
    # Labor force statistics (from LaborMarketData, but can add summary here if needed)
    # Infrastructure details (roads, ports, airports, internet connectivity)
    infrastructure_details = models.TextField(blank=True, null=True)
    economic_incentives = models.TextField(blank=True, null=True)
    geographic_advantages = models.TextField(blank=True, null=True)
    # Cost analysis (utility costs, average wages - from RealEstateData/LaborMarketData, but can add summary here)
    cost_analysis_summary = models.TextField(blank=True, null=True)
    success_stories = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Recommendation for {self.governorate.name} in {self.sector.name} sector"

    class Meta:
        unique_together = ('governorate', 'sector')
