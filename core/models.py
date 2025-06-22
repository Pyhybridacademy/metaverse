from django.db import models

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default='Investment Platform')
    site_logo = models.ImageField(upload_to='site_assets/', blank=True)
    contact_email = models.EmailField(default='admin@example.com')
    contact_phone = models.CharField(max_length=20, blank=True)
    support_chat_widget = models.TextField(blank=True, help_text='Paste your live chat widget code here')
    
    # Wallet addresses for deposits
    btc_wallet = models.CharField(max_length=200, blank=True)
    usdt_wallet = models.CharField(max_length=200, blank=True)
    eth_wallet = models.CharField(max_length=200, blank=True)
    
    # Referral settings
    referral_bonus_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    minimum_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    minimum_withdrawal = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('Only one SiteSettings instance is allowed')
        super().save(*args, **kwargs)

class CurrencyRate(models.Model):
    currency_code = models.CharField(max_length=10)  # BTC, ETH, USDT, USD, EUR, etc.
    rate_usd = models.DecimalField(max_digits=15, decimal_places=8)  # Rate in USD
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.currency_code}: ${self.rate_usd}"

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    avatar = models.ImageField(upload_to='testimonials/', blank=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.rating} stars"

class Certification(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='certifications/')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
