from django import forms
from .models import Deposit, Investment, Withdrawal, InvestmentPlan
from accounts.models import WalletAddress

class DepositForm(forms.ModelForm):
    class Meta:
        model = Deposit
        fields = ('amount', 'payment_method', 'transaction_id', 'proof_of_payment')
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter amount',
                'step': '0.01'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'transaction_id': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter transaction ID (optional)'
            }),
            'proof_of_payment': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
        }

class InvestmentForm(forms.ModelForm):
    plan = forms.ModelChoiceField(
        queryset=InvestmentPlan.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
    
    class Meta:
        model = Investment
        fields = ('plan', 'amount')
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter investment amount',
                'step': '0.01'
            }),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        plan = self.cleaned_data.get('plan')
        
        if plan:
            if amount < plan.minimum_amount:
                raise forms.ValidationError(f'Minimum investment amount is ${plan.minimum_amount}')
            if amount > plan.maximum_amount:
                raise forms.ValidationError(f'Maximum investment amount is ${plan.maximum_amount}')
        
        if amount > self.user.profile.account_balance:
            raise forms.ValidationError('Insufficient account balance')
        
        return amount

class WithdrawalForm(forms.ModelForm):
    wallet_address = forms.ModelChoiceField(
        queryset=WalletAddress.objects.none(),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
    
    class Meta:
        model = Withdrawal
        fields = ('amount', 'wallet_address')
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter withdrawal amount',
                'step': '0.01'
            }),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['wallet_address'].queryset = WalletAddress.objects.filter(user=user)
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        
        if amount > self.user.profile.account_balance:
            raise forms.ValidationError('Insufficient account balance')
        
        if amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero')
        
        return amount
