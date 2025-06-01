from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Country(models.Model):
    """Country basic information"""
    name = models.CharField(max_length=100, unique=True)
    iso_code = models.CharField(max_length=3, unique=True)
    continent = models.CharField(max_length=50)
    region = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    population = models.BigIntegerField(null=True, blank=True)
    capital = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name_plural = "Countries"
    
    def __str__(self):
        return self.name

class EconomicData(models.Model):
    """Economic indicators for countries by year"""
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='economic_data')
    year = models.IntegerField()
    
    # Inflation Metrics
    headline_inflation = models.FloatField(null=True, blank=True)
    energy_inflation = models.FloatField(null=True, blank=True)
    food_inflation = models.FloatField(null=True, blank=True)
    core_inflation = models.FloatField(null=True, blank=True)
    producer_inflation = models.FloatField(null=True, blank=True)
    gdp_deflator = models.FloatField(null=True, blank=True)
    
    # Happiness and Socioeconomic Indicators
    happiness_score = models.FloatField(null=True, blank=True)
    gdp_per_capita = models.FloatField(null=True, blank=True)
    social_support = models.FloatField(null=True, blank=True)
    healthy_life_expectancy = models.FloatField(null=True, blank=True)
    freedom_to_make_choices = models.FloatField(null=True, blank=True)
    generosity = models.FloatField(null=True, blank=True)
    perceptions_of_corruption = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['country', 'year']
        ordering = ['-year', 'country__name']
    
    def __str__(self):
        return f"{self.country.name} - {self.year}"

class TunisiaGovernorate(models.Model):
    """Tunisia governorates data"""
    name = models.CharField(max_length=100, unique=True)
    name_arabic = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    population = models.IntegerField(null=True, blank=True)
    area_km2 = models.FloatField(null=True, blank=True)
    unemployment_rate = models.FloatField(null=True, blank=True)
    agricultural_land_percentage = models.FloatField(null=True, blank=True)
    main_industries = models.TextField(blank=True)
    tourism_score = models.FloatField(null=True, blank=True)
    infrastructure_score = models.FloatField(null=True, blank=True)
    
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

class UserFavorite(models.Model):
    """User's favorite countries"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'country']
    
    def __str__(self):
        return f"{self.user.username} - {self.country.name}"
