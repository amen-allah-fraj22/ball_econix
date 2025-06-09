from django.shortcuts import render
from governorates.models import Governorate, LaborMarketData, RealEstateData
from django.db.models import Avg, Max, Min
import logging

logger = logging.getLogger(__name__)

def dashboard(request):
    # Fetch all governorates for the dropdown
    governorates = Governorate.objects.all().order_by('name')
    
    context = {
        'governorates': governorates,
        # Add other context variables as needed
    }
    
    return render(request, 'dashboard/main.html', context)

def country_comparison_select(request):
    """View for selecting governorates to compare"""
    # Fetch all Tunisian governorates
    governorates = Governorate.objects.all().order_by('name')
    
    logger.info(f"Country Comparison Select - Governorates found: {governorates.count()}")
    
    context = {
        'governorates': governorates,
    }
    
    return render(request, 'comparison/comparison_select.html', context)

def country_comparison_results(request):
    """View for displaying comparison results"""
    # Get selected governorate IDs from the form
    selected_governorate_ids = request.GET.getlist('governorates')
    
    logger.info(f"Country Comparison Results - Selected Governorate IDs: {selected_governorate_ids}")
    
    # Validate that at least 2 governorates are selected
    if len(selected_governorate_ids) < 2:
        logger.warning("Less than 2 governorates selected")
        return render(request, 'comparison/comparison_select.html', {
            'governorates': Governorate.objects.all().order_by('name'),
            'error': 'Please select at least 2 governorates to compare.'
        })
    
    # Fetch selected governorates with their latest labor market and real estate data
    compared_governorates = []
    for gov_id in selected_governorate_ids:
        try:
            governorate = Governorate.objects.get(pk=gov_id)
            
            # Get the latest labor market data
            latest_labor_data = LaborMarketData.objects.filter(
                governorate=governorate
            ).order_by('-year').first()
            
            # Get the latest real estate data
            latest_real_estate_data = RealEstateData.objects.filter(
                governorate=governorate
            ).order_by('-year').first()
            
            # Compile governorate information
            gov_info = {
                'governorate': governorate,
                'labor_data': latest_labor_data,
                'real_estate_data': latest_real_estate_data
            }
            
            compared_governorates.append(gov_info)
        
        except Governorate.DoesNotExist:
            # Skip if governorate not found
            logger.warning(f"Governorate with ID {gov_id} not found")
            continue
    
    # Prepare context for comparison template
    context = {
        'compared_governorates': compared_governorates,
        'governorates': Governorate.objects.all().order_by('name')
    }
    
    return render(request, 'comparison/comparison_results.html', context) 