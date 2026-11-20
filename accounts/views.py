# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import CustomUser, SiteSetting, Ticket, TicketMessage
from .forms import (
    PhoneForm, OTPForm, ProfileCompletionForm, PasswordLoginForm,
    ChangePasswordForm, TicketForm, TicketReplyForm
)
import random


# ============ صفحه اصلی ============
def home(request):
    setting = SiteSetting.objects.first()
    return render(request, 'index.html', {'setting': setting})


# ============ ثبت نام ============
def register_step1(request):
    setting = SiteSetting.objects.first()
    if request.method == 'POST':
        form = PhoneForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            existing_user = CustomUser.objects.filter(phone_number=phone).first()
            if existing_user:
                if existing_user.is_approved:
                    messages.info(request, "حساب شما قبلا تایید شده است. لطفا وارد شوید.")
                    return redirect('accounts:login_step1')
                else:
                    return render(request, 'accounts/pending.html', {
                        'setting': setting, 'phone': phone, 'just_registered': False
                    })

            otp = str(random.randint(100000, 999999))
            request.session['phone_number'] = phone
            request.session['otp_code'] = otp
            print(f"🔴 کد ثبت‌نام برای {phone} : {otp} 🔴")
            messages.success(request, "کد تایید به شماره شما ارسال شد.")
            return redirect('accounts:verify_otp')
    else:
        form = PhoneForm()
    return render(request, 'accounts/register.html', {'form': form, 'step': 1, 'setting': setting})


def verify_otp(request):
    setting = SiteSetting.objects.first()
    if 'phone_number' not in request.session:
        return redirect('accounts:register_step1')
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['otp_code'] == request.session.get('otp_code'):
                request.session['verified_phone'] = request.session['phone_number']
                return redirect('accounts:complete_profile')
            else:
                messages.error(request, "کد تایید اشتباه است.")
    else:
        form = OTPForm()
    return render(request, 'accounts/register.html', {'form': form, 'step': 2, 'setting': setting})


def complete_profile(request):
    setting = SiteSetting.objects.first()
    if 'verified_phone' not in request.session:
        return redirect('accounts:register_step1')
    if request.method == 'POST':
        form = ProfileCompletionForm(request.POST)
        if form.is_valid():
            phone = request.session['verified_phone']
            user, _ = CustomUser.objects.get_or_create(phone_number=phone)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.student_id = form.cleaned_data['student_id']
            user.university_name = form.cleaned_data['university_name']
            user.field_of_study = form.cleaned_data['field_of_study']
            user.set_password(form.cleaned_data['password'])
            user.is_active = True
            user.is_approved = False
            user.save()
            
            request.session.pop('phone_number', None)
            request.session.pop('otp_code', None)
            request.session.pop('verified_phone', None)
            
            return render(request, 'accounts/pending.html', {
                'setting': setting, 'phone': phone, 'just_registered': True
            })
    else:
        form = ProfileCompletionForm()
    return render(request, 'accounts/register.html', {'form': form, 'step': 3, 'setting': setting})


# ============ ورود با رمز عبور ============
def login_password(request):
    setting = SiteSetting.objects.first()
    if request.user.is_authenticated and request.user.is_approved:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = PasswordLoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            user = CustomUser.objects.filter(phone_number=phone).first()
            
            if not user:
                messages.error(request, "حساب کاربری با این شماره یافت نشد. لطفا ثبت‌نام کنید.")
                return redirect('accounts:register_step1')
            
            if not user.is_approved:
                return render(request, 'accounts/pending.html', {
                    'setting': setting, 'phone': phone, 'just_registered': False
                })
            
            if not user.has_usable_password():
                messages.error(request, "برای این حساب رمز تنظیم نشده. لطفا با کد پیامکی وارد شوید.")
                return redirect('accounts:login_otp_step1')
            
            if not user.check_password(password):
                messages.error(request, "رمز عبور اشتباه است.")
            else:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f"خوش آمدید {user.first_name or user.phone_number}!")
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard:home')
    else:
        form = PasswordLoginForm()
    
    return render(request, 'accounts/login.html', {
        'form': form, 'setting': setting, 'mode': 'password',
        'next': request.GET.get('next', '')
    })


# ============ ورود با کد پیامکی ============
def login_otp_step1(request):
    setting = SiteSetting.objects.first()
    if request.user.is_authenticated and request.user.is_approved:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = PhoneForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            user = CustomUser.objects.filter(phone_number=phone).first()
            if not user:
                messages.error(request, "حساب کاربری یافت نشد. لطفا ثبت‌نام کنید.")
                return redirect('accounts:register_step1')
            if not user.is_approved:
                return render(request, 'accounts/pending.html', {
                    'setting': setting, 'phone': phone, 'just_registered': False
                })
            
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                request.session['next_url'] = next_url
            
            otp = str(random.randint(100000, 999999))
            request.session['login_phone'] = phone
            request.session['login_otp'] = otp
            print(f"🔴 کد ورود برای {phone} : {otp} 🔴")
            messages.success(request, "کد ورود به شماره شما ارسال شد.")
            return redirect('accounts:login_otp_verify')
    else:
        form = PhoneForm()
    
    return render(request, 'accounts/login.html', {
        'form': form, 'setting': setting, 'mode': 'otp', 'step': 1,
        'next': request.GET.get('next', '')
    })


def login_otp_verify(request):
    setting = SiteSetting.objects.first()
    if 'login_phone' not in request.session:
        return redirect('accounts:login_otp_step1')
    
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['otp_code'] == request.session.get('login_otp'):
                phone = request.session['login_phone']
                user = CustomUser.objects.get(phone_number=phone)
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                request.session.pop('login_phone', None)
                request.session.pop('login_otp', None)
                messages.success(request, f"خوش آمدید {user.first_name or user.phone_number}!")
                next_url = request.session.pop('next_url', None)
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard:home')
            else:
                messages.error(request, "کد وارد شده اشتباه است.")
    else:
        form = OTPForm()
    
    return render(request, 'accounts/login.html', {
        'form': form, 'setting': setting, 'mode': 'otp', 'step': 2
    })


def logout_view(request):
    logout(request)
    messages.success(request, "با موفقیت خارج شدید.")
    return redirect('home')


# ============ تغییر رمز عبور ============
@login_required
def change_password_step1(request):
    setting = SiteSetting.objects.first()
    
    if request.method == 'POST':
        otp = str(random.randint(100000, 999999))
        request.session['change_password_otp'] = otp
        print(f"🔴 کد تغییر رمز برای {request.user.phone_number} : {otp} 🔴")
        messages.success(request, f"کد تایید به شماره {request.user.phone_number} ارسال شد.")
        return redirect('accounts:change_password_verify')
    
    return render(request, 'accounts/change_password.html', {
        'setting': setting,
        'step': 1,
    })


@login_required
def change_password_verify(request):
    setting = SiteSetting.objects.first()
    
    if 'change_password_otp' not in request.session:
        return redirect('accounts:change_password_step1')
    
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        otp_code = request.POST.get('otp_code', '').strip()
        
        if otp_code != request.session.get('change_password_otp'):
            messages.error(request, "کد تایید اشتباه است.")
        elif form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            request.session.pop('change_password_otp', None)
            login(request, request.user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "✓ رمز عبور شما با موفقیت تغییر کرد.")
            return redirect('dashboard:profile')
    else:
        form = ChangePasswordForm()
    
    return render(request, 'accounts/change_password.html', {
        'setting': setting,
        'step': 2,
        'form': form,
    })


# ============ حذف اکانت ============
@login_required
def delete_account(request):
    setting = SiteSetting.objects.first()
    
    if request.method == 'POST':
        confirm = request.POST.get('confirm', '')
        if confirm == 'DELETE':
            user = request.user
            logout(request)
            user.is_active = False
            user.is_approved = False
            user.save()
            messages.success(request, "حساب کاربری شما غیرفعال شد. در صورت نیاز با مدیر تماس بگیرید.")
            return redirect('home')
        else:
            messages.error(request, "برای تایید، کلمه DELETE را با حروف بزرگ وارد کنید.")
    
    return render(request, 'accounts/delete_account.html', {
        'setting': setting,
    })


# ============ سیستم تیکت - بخش کاربر ============
@login_required
def ticket_list(request):
    setting = SiteSetting.objects.first()
    tickets = Ticket.objects.filter(user=request.user).order_by('-updated_at')
    
    return render(request, 'accounts/ticket_list.html', {
        'setting': setting,
        'tickets': tickets,
    })


@login_required
def create_ticket(request):
    setting = SiteSetting.objects.first()
    
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = Ticket.objects.create(
                user=request.user,
                subject=form.cleaned_data['subject'],
                status='open',
            )
            TicketMessage.objects.create(
                ticket=ticket,
                sender_type='user',
                sender=request.user,
                message=form.cleaned_data['message'],
            )
            messages.success(request, "✓ تیکت شما ثبت شد. به زودی مدیر پاسخ می‌دهد.")
            return redirect('accounts:ticket_detail', pk=ticket.pk)
    else:
        form = TicketForm()
    
    return render(request, 'accounts/create_ticket.html', {
        'setting': setting,
        'form': form,
    })


@login_required
def ticket_detail(request, pk):
    setting = SiteSetting.objects.first()
    ticket = get_object_or_404(Ticket, pk=pk, user=request.user)
    
    if request.method == 'POST':
        if ticket.status == 'closed':
            messages.error(request, "این تیکت بسته شده و امکان ارسال پیام جدید وجود ندارد.")
            return redirect('accounts:ticket_detail', pk=pk)
        
        form = TicketReplyForm(request.POST)
        if form.is_valid():
            TicketMessage.objects.create(
                ticket=ticket,
                sender_type='user',
                sender=request.user,
                message=form.cleaned_data['message'],
            )
            ticket.status = 'open'
            ticket.save()
            messages.success(request, "پیام شما ارسال شد.")
            return redirect('accounts:ticket_detail', pk=pk)
    else:
        form = TicketReplyForm()
    
    return render(request, 'accounts/ticket_detail.html', {
        'setting': setting,
        'ticket': ticket,
        'messages_list': ticket.messages.all(),
        'form': form,
    })


# ============ سیستم تیکت - بخش مدیر ============
@login_required
def admin_ticket_list(request):
    if not request.user.is_staff:
        messages.error(request, "شما دسترسی به این بخش ندارید.")
        return redirect('dashboard:home')
    
    setting = SiteSetting.objects.first()
    status_filter = request.GET.get('status', '')
    
    tickets = Ticket.objects.all().select_related('user').order_by('-updated_at')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    return render(request, 'accounts/admin_ticket_list.html', {
        'setting': setting,
        'tickets': tickets,
        'status_filter': status_filter,
    })


@login_required
def admin_ticket_detail(request, pk):
    if not request.user.is_staff:
        messages.error(request, "شما دسترسی به این بخش ندارید.")
        return redirect('dashboard:home')
    
    setting = SiteSetting.objects.first()
    ticket = get_object_or_404(Ticket, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action', 'reply')
        
        if action == 'reply':
            form = TicketReplyForm(request.POST)
            if form.is_valid():
                TicketMessage.objects.create(
                    ticket=ticket,
                    sender_type='admin',
                    sender=request.user,
                    message=form.cleaned_data['message'],
                )
                ticket.status = 'answered'
                ticket.save()
                messages.success(request, "پاسخ شما ارسال شد.")
                return redirect('accounts:admin_ticket_detail', pk=pk)
        
        elif action == 'close':
            ticket.status = 'closed'
            ticket.save()
            messages.success(request, "تیکت بسته شد.")
            return redirect('accounts:admin_ticket_detail', pk=pk)
        
        elif action == 'reopen':
            ticket.status = 'open'
            ticket.save()
            messages.success(request, "تیکت بازگشایی شد.")
            return redirect('accounts:admin_ticket_detail', pk=pk)
    else:
        form = TicketReplyForm()
    
    return render(request, 'accounts/admin_ticket_detail.html', {
        'setting': setting,
        'ticket': ticket,
        'messages_list': ticket.messages.all(),
        'form': form,
    })