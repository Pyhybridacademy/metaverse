import requests
from decimal import Decimal
from django.utils import timezone
from .models import CurrencyRate

def get_currency_rates():
    """Fetch live currency rates from external API"""
    try:
        # Using CoinGecko API as an example (free tier)
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'bitcoin,ethereum,tether',
            'vs_currencies': 'usd'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # Update or create currency rates
        currency_mapping = {
            'bitcoin': 'BTC',
            'ethereum': 'ETH',
            'tether': 'USDT'
        }
        
        for coin_id, currency_code in currency_mapping.items():
            if coin_id in data and 'usd' in data[coin_id]:
                rate, created = CurrencyRate.objects.get_or_create(
                    currency_code=currency_code,
                    defaults={'rate_usd': Decimal(str(data[coin_id]['usd']))}
                )
                if not created:
                    rate.rate_usd = Decimal(str(data[coin_id]['usd']))
                    rate.save()
        
        return True
    except Exception as e:
        print(f"Error fetching currency rates: {e}")
        return False

def calculate_roi(investment_amount, roi_percentage):
    """Calculate ROI amount"""
    return (investment_amount * roi_percentage) / 100

def format_currency(amount, currency_code='USD'):
    """Format currency amount"""
    if currency_code == 'USD':
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency_code}"
