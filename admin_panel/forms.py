from django import forms
from django.contrib.auth.models import User
from accounts.models import UserProfile

class AdminProfileForm(forms.ModelForm):
    full_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'country', 'state', 'address']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
                'placeholder': 'Enter your phone number'
            }),
            'country': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent'
            }),
            'state': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
                'placeholder': 'Enter your state/province'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Enter your full address'
            }),
        }