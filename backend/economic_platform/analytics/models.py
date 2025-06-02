from django.db import models
from tunisia.models import TunisiaGovernorate

class LaborMarketData(models.Model):
    governorate = models.ForeignKey(TunisiaGovernorate, on_delete=models.CASCADE, related_name='labor_market_data')
    year = models.IntegerField()
    unemployment_rate = models.FloatField(null=True, blank=True)
    youth_unemployment = models.FloatField(null=True, blank=True)
    female_unemployment = models.FloatField(null=True, blank=True)
    labor_force_participation = models.FloatField(null=True, blank=True)
    average_wage = models.FloatField(null=True, blank=True)
    job_creation_rate = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ['governorate', 'year']
        verbose_name_plural = "Labor Market Data"

    def __str__(self):
        return f"{self.governorate.name} - {self.year} Labor Data"
