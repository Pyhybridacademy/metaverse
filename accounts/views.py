from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from .forms import RegistrationStep1Form, RegistrationStep2Form, KYCUploadForm, ProfileUpdateForm
from .models import CustomUser, WalletAddress, Referral, UserProfile
from core.models import SiteSettings

def register_step1(request):
    if request.method == 'POST':
        form = RegistrationStep1Form(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.registration_step = 1
            user.save()
            
            # Save wallet addresses
            WalletAddress.objects.create(
                user=user,
                wallet_type='USDT',
                address=form.cleaned_data['usdt_wallet'],
                is_primary=True
            )
            WalletAddress.objects.create(
                user=user,
                wallet_type='BTC',
                address=form.cleaned_data['btc_wallet']
            )
            
            # Log the user in and redirect to step 2
            login(request, user)
            return redirect('accounts:register_step2')
    else:
        form = RegistrationStep1Form()
    
    return render(request, 'auth/register_step1.html', {'form': form})

@login_required
def register_step2(request):
    if request.user.registration_step != 1:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = RegistrationStep2Form(request.POST, instance=request.user.profile)
        kyc_form = KYCUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            profile = form.save()
            
            # Handle referral code
            referral_code = form.cleaned_data.get('referral_code')
            if referral_code:
                try:
                    referrer_profile = UserProfile.objects.get(referral_code=referral_code)
                    Referral.objects.create(
                        referrer=referrer_profile.user,
                        referred=request.user
                    )
                    profile.referred_by = referrer_profile
                    profile.save()
                except UserProfile.DoesNotExist:
                    messages.warning(request, 'Invalid referral code.')
            
            # Handle KYC upload if provided
            if kyc_form.is_valid() and request.FILES.get('document_file'):
                kyc = kyc_form.save(commit=False)
                kyc.user = request.user
                kyc.save()
            
            # Update registration step
            request.user.registration_step = 2
            request.user.save()
            
            messages.success(request, 'Registration completed! Your account is pending approval.')
            return redirect('core:dashboard')
    else:
        form = RegistrationStep2Form(instance=request.user.profile)
        kyc_form = KYCUploadForm()
    
    return render(request, 'auth/register_step2.html', {
        'form': form,
        'kyc_form': kyc_form
    })

@login_required
def profile(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'profile':
            form = ProfileUpdateForm(request.POST, instance=request.user.profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('accounts:profile')
        
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    
    return render(request, 'dashboard/profile.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})

def password_reset_request(request):
    """Custom password reset request view"""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(email=email, is_active=True)
                
                # Generate token and uid
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Get site settings for email context
                try:
                    site_settings = SiteSettings.objects.first()
                    site_name = site_settings.site_name if site_settings else 'Investment Platform'
                    contact_email = site_settings.contact_email if site_settings else settings.DEFAULT_FROM_EMAIL
                except:
                    site_name = 'Investment Platform'
                    contact_email = settings.DEFAULT_FROM_EMAIL
                
                # Build reset URL
                current_site = get_current_site(request)
                reset_url = request.build_absolute_uri(
                    reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )
                
                # Email context
                context = {
                    'user': user,
                    'site_name': site_name,
                    'reset_url': reset_url,
                    'domain': current_site.domain,
                    'protocol': 'https' if request.is_secure() else 'http',
                }
                
                # Send email
                subject = f'Password Reset for {site_name}'
                message = render_to_string('registration/password_reset_email.html', context)
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=contact_email,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                messages.success(request, 'Password reset email has been sent to your email address.')
                return redirect('accounts:password_reset_done')
                
            except CustomUser.DoesNotExist:
                # Don't reveal if email exists or not for security
                messages.success(request, 'If an account with that email exists, a password reset email has been sent.')
                return redirect('accounts:password_reset_done')
            except Exception as e:
                messages.error(request, 'An error occurred while sending the email. Please try again.')
    else:
        form = PasswordResetForm()
    
    return render(request, 'registration/password_reset_form.html', {'form': form})

def password_reset_done(request):
    """Password reset email sent confirmation"""
    return render(request, 'registration/password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    """Password reset confirmation view"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully!')
                return redirect('accounts:password_reset_complete')
        else:
            form = SetPasswordForm(user)
    else:
        validlink = False
        form = None
        messages.error(request, 'The password reset link is invalid or has expired.')
    
    return render(request, 'registration/password_reset_confirm.html', {
        'form': form,
        'validlink': validlink,
    })

def password_reset_complete(request):
    """Password reset complete view"""
    return render(request, 'registration/password_reset_complete.html')

@login_required
def referrals(request):
    referrals = Referral.objects.filter(referrer=request.user).select_related('referred')
    return render(request, 'dashboard/referrals.html', {'referrals': referrals})

@login_required
def wallets(request):
    wallets = WalletAddress.objects.filter(user=request.user)
    return render(request, 'dashboard/wallets.html', {'wallets': wallets})