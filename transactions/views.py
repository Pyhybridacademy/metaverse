from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Deposit, Investment, Withdrawal, Transaction, InvestmentPlan
from .forms import DepositForm, InvestmentForm, WithdrawalForm

@login_required
def deposits(request):
    user_deposits = Deposit.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'transactions/deposits.html', {'deposits': user_deposits})

@login_required
def new_deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST, request.FILES)
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.user = request.user
            deposit.save()
            
            # Create transaction record
            Transaction.objects.create(
                user=request.user,
                transaction_type='deposit',
                amount=deposit.amount,
                description=f'Deposit via {deposit.payment_method}',
                reference_id=str(deposit.id)
            )
            
            messages.success(request, 'Deposit request submitted successfully! Awaiting approval.')
            return redirect('transactions:deposits')
    else:
        form = DepositForm()
    
    return render(request, 'transactions/new_deposit.html', {'form': form})

@login_required
def investments(request):
    user_investments = Investment.objects.filter(user=request.user).order_by('-start_date')
    return render(request, 'transactions/investments.html', {'investments': user_investments})

@login_required
def new_investment(request):
    if request.method == 'POST':
        form = InvestmentForm(request.user, request.POST)
        if form.is_valid():
            with transaction.atomic():
                investment = form.save(commit=False)
                investment.user = request.user
                investment.end_date = timezone.now() + timedelta(days=investment.plan.duration_days)
                investment.save()
                
                # Deduct from account balance
                profile = request.user.profile
                profile.account_balance -= investment.amount
                profile.current_investment += investment.amount
                profile.save()
                
                # Create transaction record
                Transaction.objects.create(
                    user=request.user,
                    transaction_type='investment',
                    amount=-investment.amount,
                    description=f'Investment in {investment.plan.name}',
                    reference_id=str(investment.id)
                )
                
                messages.success(request, f'Investment of ${investment.amount} in {investment.plan.name} created successfully!')
                return redirect('transactions:investments')
    else:
        form = InvestmentForm(request.user)
    
    investment_plans = InvestmentPlan.objects.filter(is_active=True)
    return render(request, 'transactions/new_investment.html', {
        'form': form,
        'investment_plans': investment_plans
    })

@login_required
def withdrawals(request):
    user_withdrawals = Withdrawal.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'transactions/withdrawals.html', {'withdrawals': user_withdrawals})

@login_required
def new_withdrawal(request):
    if request.method == 'POST':
        form = WithdrawalForm(request.user, request.POST)
        if form.is_valid():
            with transaction.atomic():
                withdrawal = form.save(commit=False)
                withdrawal.user = request.user
                wallet = form.cleaned_data['wallet_address']
                withdrawal.wallet_address = wallet.address
                withdrawal.wallet_type = wallet.wallet_type
                withdrawal.save()
                
                # Update pending withdrawal
                profile = request.user.profile
                profile.pending_withdrawal += withdrawal.amount
                profile.save()
                
                # Create transaction record
                Transaction.objects.create(
                    user=request.user,
                    transaction_type='withdrawal',
                    amount=-withdrawal.amount,
                    description=f'Withdrawal to {withdrawal.wallet_type} wallet',
                    reference_id=str(withdrawal.id)
                )
                
                messages.success(request, 'Withdrawal request submitted successfully! Awaiting approval.')
                return redirect('transactions:withdrawals')
    else:
        form = WithdrawalForm(request.user)
    
    return render(request, 'transactions/new_withdrawal.html', {'form': form})

@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'transactions/history.html', {'transactions': transactions})
