from .utils import calculate_investment_stats

def investment_stats(request):
    """Add investment statistics to template context"""
    if request.user.is_authenticated and request.user.is_staff:
        return {
            'investment_stats': calculate_investment_stats()
        }
    return {}