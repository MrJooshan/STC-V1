# dashboard/views.py
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, IntegerField, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from accounts.models import SiteSetting, CustomUser


@login_required
def home(request):
    setting = SiteSetting.objects.first()
    
    if not request.user.is_approved:
        return render(request, 'accounts/pending.html', {
            'setting': setting,
            'phone': request.user.phone_number
        })
    
    # ==========================================
    # مسابقات (بدون فیلتر زمانی - همه فعال‌ها)
    # ==========================================
    from competitions.models import Competition
    active_competitions = Competition.objects.filter(
        is_active=True
    ).order_by('start_datetime')
    
    # ==========================================
    # دسته‌بندی‌ها با ۳ آزمون برتر
    # ==========================================
    from exams.models import Category, Exam
    categories_data = []
    for cat in Category.objects.all():
        top_exams = Exam.objects.filter(
            category=cat, is_approved=True
        ).annotate(
            attempts_count=Count('attempts')
        ).order_by('-attempts_count', '-created_at')[:3]
        
        if top_exams.exists():
            total_count = Exam.objects.filter(category=cat, is_approved=True).count()
            categories_data.append({
                'category': cat,
                'exams': top_exams,
                'total': total_count,
            })
    
    # ==========================================
    # برترین کاربران
    # ==========================================
    top_users = CustomUser.objects.filter(
        is_approved=True, is_active=True
    ).order_by('-points', 'date_joined')[:10]
    
    return render(request, 'dashboard/home.html', {
        'user': request.user,
        'setting': setting,
        'active_competitions': active_competitions,
        'categories_data': categories_data,
        'top_users': top_users,
        'active_page': 'home',
    })
    
    # ==========================================
    # برترین کاربران
    # ==========================================
    top_users = CustomUser.objects.filter(
        is_approved=True, is_active=True
    ).order_by('-points', 'date_joined')[:10]
    
    return render(request, 'dashboard/home.html', {
        'user': request.user,
        'setting': setting,
        'active_competitions': active_competitions,
        'categories_data': categories_data,
        'top_users': top_users,
        'active_page': 'home',
    })


@login_required
def profile(request):
    setting = SiteSetting.objects.first()
    
    if not request.user.is_approved:
        return render(request, 'accounts/pending.html', {
            'setting': setting,
            'phone': request.user.phone_number
        })
    
    # آمار آزمون‌ها
    user_attempts = request.user.attempts.filter(is_completed=True)
    total_attempts = user_attempts.count()
    perfect_attempts = user_attempts.filter(score__gt=0).count()
    created_exams_count = request.user.created_exams.count()
    
    # آمار رقابت
    rivalry_wins = request.user.rivalry_wins
    rivalry_losses = request.user.rivalry_losses
    total_rivalries = rivalry_wins + rivalry_losses
    win_rate = round((rivalry_wins / total_rivalries * 100)) if total_rivalries > 0 else 0
    
    # محاسبه رتبه کاربر
    rank = CustomUser.objects.filter(
        is_approved=True,
        is_active=True,
        points__gt=request.user.points
    ).count() + 1
    
    return render(request, 'dashboard/profile.html', {
        'user': request.user,
        'setting': setting,
        'total_attempts': total_attempts,
        'perfect_attempts': perfect_attempts,
        'created_exams_count': created_exams_count,
        'rank': rank,
        'rivalry_wins': rivalry_wins,
        'rivalry_losses': rivalry_losses,
        'total_rivalries': total_rivalries,
        'win_rate': win_rate,
        'active_page': 'profile',
    })


@login_required
def ranking(request):
    setting = SiteSetting.objects.first()
    
    if not request.user.is_approved:
        return render(request, 'accounts/pending.html', {
            'setting': setting,
            'phone': request.user.phone_number
        })
    
    # گرفتن همه کاربران تایید شده با آمار تفکیکی
    users_qs = CustomUser.objects.filter(
        is_approved=True,
        is_active=True
    ).annotate(
        easy_points=Coalesce(
            Sum('attempts__score', filter=Q(
                attempts__exam__difficulty='easy',
                attempts__is_completed=True,
                attempts__score__gt=0,
            )),
            Value(0), output_field=IntegerField()
        ),
        medium_points=Coalesce(
            Sum('attempts__score', filter=Q(
                attempts__exam__difficulty='medium',
                attempts__is_completed=True,
                attempts__score__gt=0,
            )),
            Value(0), output_field=IntegerField()
        ),
        hard_points=Coalesce(
            Sum('attempts__score', filter=Q(
                attempts__exam__difficulty='hard',
                attempts__is_completed=True,
                attempts__score__gt=0,
            )),
            Value(0), output_field=IntegerField()
        ),
    ).order_by('-points', 'date_joined', 'id')
    
    ranked_users = []
    current_user_rank = None
    
    for idx, u in enumerate(users_qs, start=1):
        item = {'rank': idx, 'user': u, 'is_current': u.pk == request.user.pk}
        if item['is_current']:
            current_user_rank = idx
        ranked_users.append(item)
    
    top_3 = ranked_users[:3]
    rest_users = ranked_users[3:50]
    
    current_user_data = None
    if current_user_rank is None or current_user_rank > 50:
        for item in ranked_users:
            if item['is_current']:
                current_user_data = item
                break
    
    return render(request, 'dashboard/ranking.html', {
        'setting': setting,
        'top_3': top_3,
        'rest_users': rest_users,
        'current_user_rank': current_user_rank,
        'current_user_data': current_user_data,
        'total_users': len(ranked_users),
        'active_page': 'ranking',
    })