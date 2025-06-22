from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('deposits/', views.deposits, name='deposits'),
    path('deposits/new/', views.new_deposit, name='new_deposit'),
    path('investments/', views.investments, name='investments'),
    path('investments/new/', views.new_investment, name='new_investment'),
    path('withdrawals/', views.withdrawals, name='withdrawals'),
    path('withdrawals/new/', views.new_withdrawal, name='new_withdrawal'),
    path('history/', views.transaction_history, name='history'),
]
