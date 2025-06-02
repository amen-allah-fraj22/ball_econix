from django.db import models

class TunisiaGovernorate(models.Model):
    """Tunisia governorates data"""
    name = models.CharField(max_length=100, unique=True)
    arabic_name = models.CharField(max_length=100, blank=True) # Renamed from name_arabic
    latitude = models.FloatField()
    longitude = models.FloatField()
    population_2024 = models.IntegerField(null=True, blank=True) # Renamed from population
    area_km2 = models.FloatField(null=True, blank=True)
    unemployment_rate = models.FloatField(null=True, blank=True)
    agricultural_land_percent = models.FloatField(null=True, blank=True) # Renamed
    population_density = models.FloatField(null=True, blank=True) # Added
    labor_force_size = models.IntegerField(null=True, blank=True) # Added
    gdp_contribution = models.FloatField(null=True, blank=True) # Added
    coastal_access = models.BooleanField(default=False) # Added
    industrial_zones = models.IntegerField(null=True, blank=True) # Added
    tourist_attractions = models.IntegerField(null=True, blank=True) # Added
    # Removed: main_industries, tourism_score, infrastructure_score

    def __str__(self):
        return self.name

class InvestmentScore(models.Model):
    """Investment scores for Tunisia governorates by sector"""
    SECTOR_CHOICES = [
        ('agriculture', 'Agriculture'),
        ('tourism', 'Tourism'),
        ('manufacturing', 'Manufacturing'),
        ('technology', 'Technology'),
        ('services', 'Services'),
    ]

    governorate = models.ForeignKey(TunisiaGovernorate, on_delete=models.CASCADE, related_name='investment_scores')
    sector = models.CharField(max_length=20, choices=SECTOR_CHOICES)
    overall_score = models.FloatField()
    labor_score = models.FloatField(null=True, blank=True)
    infrastructure_score = models.FloatField(null=True, blank=True)
    tax_incentive_score = models.FloatField(null=True, blank=True)
    market_access_score = models.FloatField(null=True, blank=True)
    reasoning = models.TextField(blank=True)
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['governorate', 'sector']

    def __str__(self):
        return f"{self.governorate.name} - {self.sector} ({self.overall_score})"

class RealEstatePrices(models.Model):
    governorate = models.ForeignKey(TunisiaGovernorate, on_delete=models.CASCADE, related_name='real_estate_prices')
    year = models.IntegerField()
    residential_price_per_m2 = models.FloatField(null=True, blank=True)
    commercial_price_per_m2 = models.FloatField(null=True, blank=True)
    land_price_per_m2 = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ['governorate', 'year']

    def __str__(self):
        return f"{self.governorate.name} - {self.year} Real Estate"

class TaxIncentives(models.Model):
    governorate = models.ForeignKey(TunisiaGovernorate, on_delete=models.CASCADE, related_name='tax_incentives')
    sector = models.CharField(max_length=50)  # e.g., agriculture, tourism, manufacturing
    incentive_type = models.CharField(max_length=100)
    tax_reduction_percent = models.FloatField(null=True, blank=True)
    duration_years = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ['governorate', 'sector', 'incentive_type']

    def __str__(self):
        return f"{self.governorate.name} - {self.sector} - {self.incentive_type}"


class LaborMarketData(models.Model):
    governorate = models.ForeignKey(TunisiaGovernorate, on_delete=models.CASCADE, related_name='tunisia_labor_market_data')
    year = models.IntegerField()
    unemployment_rate = models.FloatField(null=True, blank=True)
    youth_unemployment = models.FloatField(null=True, blank=True)
    female_unemployment = models.FloatField(null=True, blank=True)
    labor_force_participation = models.FloatField(null=True, blank=True)
    average_wage = models.FloatField(null=True, blank=True)
    job_creation_rate = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ['governorate', 'year']

    def __str__(self):
        return f"{self.governorate.name} - {self.year} Labor Data"
