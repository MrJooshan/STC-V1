# competitions/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.models import SiteSetting
from .models import Competition
from .forms import CompetitionForm


# ==========================================
# بخش ادمین - فقط staff
# ==========================================
def staff_required(view_func):
    """دکوراتور برای محدود کردن به ادمین"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, "شما دسترسی به این بخش ندارید.")
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@staff_required
def admin_competition_list(request):
    """لیست مسابقات (پنل ادمین)"""
    setting = SiteSetting.objects.first()
    competitions = Competition.objects.all().order_by('-start_datetime')
    
    return render(request, 'competitions/admin_list.html', {
        'setting': setting,
        'competitions': competitions,
    })


@login_required
@staff_required
def admin_competition_create(request):
    """ساخت مسابقه جدید"""
    setting = SiteSetting.objects.first()
    
    if request.method == 'POST':
        form = CompetitionForm(request.POST, request.FILES)
        if form.is_valid():
            competition = form.save(commit=False)
            competition.created_by = request.user
            competition.save()
            messages.success(request, f"✓ مسابقه «{competition.title}» با موفقیت ساخته شد.")
            return redirect('competitions:admin_list')
    else:
        form = CompetitionForm()
    
    return render(request, 'competitions/admin_form.html', {
        'setting': setting,
        'form': form,
        'action': 'create',
    })


@login_required
@staff_required
def admin_competition_edit(request, pk):
    """ویرایش مسابقه"""
    setting = SiteSetting.objects.first()
    competition = get_object_or_404(Competition, pk=pk)
    
    if request.method == 'POST':
        form = CompetitionForm(request.POST, request.FILES, instance=competition)
        if form.is_valid():
            form.save()
            messages.success(request, "✓ مسابقه با موفقیت ویرایش شد.")
            return redirect('competitions:admin_list')
    else:
        form = CompetitionForm(instance=competition)
    
    return render(request, 'competitions/admin_form.html', {
        'setting': setting,
        'form': form,
        'competition': competition,
        'action': 'edit',
    })


@login_required
@staff_required
def admin_competition_delete(request, pk):
    """حذف مسابقه"""
    competition = get_object_or_404(Competition, pk=pk)
    
    if request.method == 'POST':
        title = competition.title
        competition.delete()
        messages.success(request, f"مسابقه «{title}» حذف شد.")
        return redirect('competitions:admin_list')
    
    return render(request, 'competitions/admin_delete.html', {
        'setting': SiteSetting.objects.first(),
        'competition': competition,
    })


# ==========================================
# نمایش عمومی (برای کاربران)
# ==========================================
@login_required
def competition_detail(request, pk):
    """مشاهده جزئیات مسابقه (همه کاربران)"""
    setting = SiteSetting.objects.first()
    competition = get_object_or_404(Competition, pk=pk, is_active=True)
    
    return render(request, 'competitions/detail.html', {
        'setting': setting,
        'competition': competition,
    })



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.models import SiteSetting, CustomUser
from .models import Competition, CompetitionQuestion, CompetitionAttempt, CompetitionAnswer
from .forms import CompetitionForm, CompetitionQuestionForm


# ==========================================
# مدیریت سوالات (ادمین)
# ==========================================
@login_required
@staff_required
def manage_questions(request, pk):
    setting = SiteSetting.objects.first()
    competition = get_object_or_404(Competition, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_question':
            form = CompetitionQuestionForm(request.POST)
            if form.is_valid():
                q = form.save(commit=False)
                q.competition = competition
                q.save()
                messages.success(request, "سوال اضافه شد.")
                return redirect('competitions:manage_questions', pk=pk)
        
        elif action == 'delete_question':
            qid = request.POST.get('question_id')
            CompetitionQuestion.objects.filter(pk=qid, competition=competition).delete()
            messages.success(request, "سوال حذف شد.")
            return redirect('competitions:manage_questions', pk=pk)
    
    return render(request, 'competitions/manage_questions.html', {
        'setting': setting,
        'competition': competition,
        'questions': competition.questions.all(),
        'form': CompetitionQuestionForm(),
    })


# ==========================================
# شرکت در مسابقه (کاربر)
# ==========================================
@login_required
def take_competition(request, pk):
    setting = SiteSetting.objects.first()
    if not request.user.is_approved:
        return redirect('accounts:login_step1')
    
    competition = get_object_or_404(Competition, pk=pk, is_active=True)
    
    # چک زمان
    if competition.status != 'live':
        messages.warning(request, "این مسابقه در حال حاضر فعال نیست.")
        return redirect('competitions:detail', pk=pk)
    
    # چک شرکت قبلی
    existing = CompetitionAttempt.objects.filter(
        user=request.user, competition=competition, is_completed=True
    ).first()
    if existing:
        messages.info(request, "شما قبلاً در این مسابقه شرکت کرده‌اید.")
        return redirect('competitions:result', pk=pk, attempt_id=existing.pk)
    
    questions = competition.questions.all()
    if not questions.exists():
        messages.warning(request, "این مسابقه هنوز سوالی ندارد.")
        return redirect('competitions:detail', pk=pk)
    
    if request.method == 'POST':
        attempt = CompetitionAttempt.objects.create(
            user=request.user, competition=competition,
            total_points=questions.count(),
        )
        score = 0
        for q in questions:
            sel = request.POST.get(f'question_{q.id}')
            if not sel: continue
            try:
                sel_int = int(sel)
                if sel_int not in [1,2,3,4]: continue
            except: continue
            is_correct = (sel_int == q.correct_option)
            if is_correct: score += 1
            CompetitionAnswer.objects.create(
                attempt=attempt, question=q,
                selected_option=sel_int, is_correct=is_correct,
            )
        attempt.score = score
        attempt.is_completed = True
        attempt.completed_at = timezone.now()
        attempt.save()
        messages.success(request, "✓ پاسخ‌های شما ثبت شد!")
        return redirect('competitions:result', pk=pk, attempt_id=attempt.pk)
    
    return render(request, 'competitions/take.html', {
        'setting': setting,
        'competition': competition,
        'questions': questions,
    })


# ==========================================
# نتیجه مسابقه
# ==========================================
@login_required
def competition_result(request, pk, attempt_id):
    setting = SiteSetting.objects.first()
    competition = get_object_or_404(Competition, pk=pk)
    attempt = get_object_or_404(CompetitionAttempt, pk=attempt_id, user=request.user, competition=competition)
    answers = attempt.answers.select_related('question').all()
    
    # رتبه کاربر توی این مسابقه
    all_attempts = CompetitionAttempt.objects.filter(
        competition=competition, is_completed=True
    ).order_by('-score', 'completed_at')
    
    user_rank = None
    for idx, a in enumerate(all_attempts, start=1):
        if a.pk == attempt.pk:
            user_rank = idx
            break
    
    return render(request, 'competitions/result.html', {
        'setting': setting,
        'competition': competition,
        'attempt': attempt,
        'answers': answers,
        'user_rank': user_rank,
        'total_participants': all_attempts.count(),
    })


@login_required
def competition_list(request):
    setting = SiteSetting.objects.first()
    if not request.user.is_approved:
        return redirect('accounts:login_step1')
    
    competitions = Competition.objects.filter(is_active=True).order_by('start_datetime')
    
    return render(request, 'competitions/list.html', {
        'setting': setting,
        'competitions': competitions,
    })