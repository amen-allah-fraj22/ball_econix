from django.contrib import admin
from .models import TunisiaGovernorate, InvestmentScore, RealEstatePrices, TaxIncentives, LaborMarketData

admin.site.register(TunisiaGovernorate)
admin.site.register(InvestmentScore)
admin.site.register(LaborMarketData)
# admin.site.register(RealEstatePrices) # Not explicitly requested to register these yet
# admin.site.register(TaxIncentives)   # Not explicitly requested to register these yet
