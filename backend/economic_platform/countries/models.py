from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Country(models.Model):
    """Country basic information"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)
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

class EconomicIndicator(models.Model):
    """Economic indicators for countries by year"""
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='economic_indicators')
    year = models.IntegerField()
    
    # Inflation Metrics
    headline_consumer_price_inflation = models.FloatField(null=True, blank=True)
    energy_consumer_price_inflation = models.FloatField(null=True, blank=True)
    food_consumer_price_inflation = models.FloatField(null=True, blank=True)
    official_core_consumer_price_inflation = models.FloatField(null=True, blank=True)
    producer_price_inflation = models.FloatField(null=True, blank=True)
    gdp_deflator_index_growth_rate = models.FloatField(null=True, blank=True)
    
    # Happiness and Socioeconomic Indicators
    happiness_score = models.FloatField(null=True, blank=True)
    gdp_per_capita = models.FloatField(null=True, blank=True)
    social_support = models.FloatField(null=True, blank=True)
    healthy_life_expectancy_at_birth = models.FloatField(null=True, blank=True)
    freedom_to_make_life_choices = models.FloatField(null=True, blank=True)
    generosity = models.FloatField(null=True, blank=True)
    perceptions_of_corruption = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['country', 'year']
        ordering = ['-year', 'country__name']
    
    def __str__(self):
        return f"{self.country.name} - {self.year} Economic Indicators"

class UserFavorite(models.Model):
    """User's favorite countries"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'country']
    
    def __str__(self):
        return f"{self.user.username} - {self.country.name}"
