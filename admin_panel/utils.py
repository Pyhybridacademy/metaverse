from django.db.models import Sum, Count
from django.contrib.auth import get_user_model
from transactions.models import Investment, Deposit, Withdrawal

User = get_user_model()

def calculate_investment_stats():
    """Calculate investment statistics for admin context processor"""
    try:
        stats = {
            'total_investments': Investment.objects.count(),
            'active_investments': Investment.objects.filter(status='active').count(),
            'completed_investments': Investment.objects.filter(status='completed').count(),
            'total_investment_amount': Investment.objects.aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'total_expected_returns': Investment.objects.aggregate(
                total=Sum('expected_return')
            )['total'] or 0,
            'pending_deposits': Deposit.objects.filter(status='pending').count(),
            'pending_withdrawals': Withdrawal.objects.filter(status='pending').count(),
            'total_users': User.objects.filter(is_staff=False).count(),
        }
        return stats
    except Exception:
        # Return empty stats if there's any error
        return {
            'total_investments': 0,
            'active_investments': 0,
            'completed_investments': 0,
            'total_investment_amount': 0,
            'total_expected_returns': 0,
            'pending_deposits': 0,
            'pending_withdrawals': 0,
            'total_users': 0,
        }
