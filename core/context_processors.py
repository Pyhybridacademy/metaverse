from .models import SiteSettings, CurrencyRate
from .utils import get_currency_rates

def site_settings(request):
    """Add site settings to template context"""
    try:
        settings = SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        settings = None
    
    return {'site_settings': settings}

def currency_rates(request):
    """Add currency rates to template context"""
    rates = {}
    try:
        currency_rates = CurrencyRate.objects.all()
        for rate in currency_rates:
            rates[rate.currency_code] = rate.rate_usd
    except:
        pass
    
    return {'currency_rates': rates}
