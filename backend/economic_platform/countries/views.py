from django.shortcuts import render, get_object_or_404
from .models import Country, EconomicIndicator

# Create your views here.

def country_detail(request, country_name):
    country = get_object_or_404(Country, name__iexact=country_name)
    indicators = EconomicIndicator.objects.filter(country=country).order_by('year')

    context = {
        'country': country,
        'economic_indicators': indicators
    }
    return render(request, 'countries/country_detail.html', context)
