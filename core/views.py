from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from transactions.models import Transaction, Investment, Deposit, Withdrawal
from accounts.models import Referral
from .models import Testimonial, Certification
from .utils import get_currency_rates
from core.models import SiteSettings, Testimonial, Certification
from transactions.models import InvestmentPlan
User = get_user_model()



def home(request):
    """Render the homepage with dynamic content"""
    site_settings = SiteSettings.objects.first()
    testimonials = Testimonial.objects.filter(is_active=True).order_by('-created_at')[:6]
    certifications = Certification.objects.filter(is_active=True).order_by('-created_at')
    investment_plans = InvestmentPlan.objects.filter(is_active=True).order_by('minimum_amount')

    context = {
        'site_settings': site_settings,
        'testimonials': testimonials,
        'certifications': certifications,
        'investment_plans': investment_plans,
        'total_users': 5000,  # Replace with actual User.objects.count() if needed
        'total_invested': 2500000,  # Replace with actual aggregate if needed
    }
    return render(request, 'core/home.html', context)

@login_required
def dashboard(request):
    """User dashboard"""
    user = request.user
    profile = user.profile
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(user=user)[:10]
    
    # Get active investments
    active_investments = Investment.objects.filter(user=user, status='active')
    
    # Get pending items
    pending_deposits = Deposit.objects.filter(user=user, status='pending').count()
    pending_withdrawals = Withdrawal.objects.filter(user=user, status='pending').count()
    
    # Update currency rates (optional, can be done via cron job)
    get_currency_rates()
    
    context = {
        'profile': profile,
        'recent_transactions': recent_transactions,
        'active_investments': active_investments,
        'pending_deposits': pending_deposits,
        'pending_withdrawals': pending_withdrawals,
    }
    
    return render(request, 'dashboard/index.html', context)
