# exams/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from accounts.models import SiteSetting
from .models import Category, Exam, ExamPage, Question, ExamAttempt, UserAnswer
from .forms import ExamForm, ExamPageForm, QuestionForm


# ==========================================
# امتیاز بر اساس سطح سختی
# ==========================================
DIFFICULTY_POINTS = {
    'easy': 1,
    'medium': 2,
    'hard': 3,
}


# ==========================================
# لیست آزمون‌ها (با جستجو و دسته‌بندی)
# ==========================================
@login_required
def exam_list(request):
    setting = SiteSetting.objects.first()
    if not request.user.is_approved:
        return redirect('accounts:login_step1')
    
    exams = Exam.objects.filter(is_approved=True).select_related('author', 'category')
    
    # جستجو
    q = request.GET.get('q', '').strip()
    if q:
        exams = exams.filter(Q(title__icontains=q) | Q(description__icontains=q))
    
    # فیلتر دسته‌بندی
    category_id = request.GET.get('category')
    if category_id:
        exams = exams.filter(category_id=category_id)
    
    categories = Category.objects.all()
    
    return render(request, 'exams/list.html', {
        'setting': setting,
        'exams': exams,
        'categories': categories,
        'search_query': q,
        'selected_category': category_id,
        'active_page': 'exams',
    })


# ==========================================
# جزئیات آزمون (قبل از شروع)
# ==========================================
@login_required
def exam_detail(request, pk):
    setting = SiteSetting.objects.first()
    if not request.user.is_approved:
        return redirect('accounts:login_step1')
    
    exam = get_object_or_404(Exam, pk=pk, is_approved=True)
    
    # چک می‌کنیم آیا کاربر نویسنده است
    is_author = (exam.author_id == request.user.id)
    
    # بررسی شرکت قبلی
    previous_attempts = ExamAttempt.objects.filter(
        user=request.user, exam=exam, is_completed=True
    ).order_by('-completed_at')
    
    has_attempted = previous_attempts.exists()
    best_attempt = previous_attempts.first() if has_attempted else None
    
    return render(request, 'exams/detail.html', {
        'setting': setting,
        'exam': exam,
        'previous_attempts': previous_attempts[:3],
        'has_attempted': has_attempted,
        'best_attempt': best_attempt,
        'is_author': is_author,
        'active_page': 'exams',
    })


# ==========================================
# مطالعه صفحه به صفحه
# ==========================================
@login_required
def study_page(request, pk, page_num=1):
    setting = SiteSetting.objects.first()
    if not request.user.is_approved:
        return redirect('accounts:login_step1')
    
    exam = get_object_or_404(Exam, pk=pk, is_approved=True)
    
    # نویسنده نمی‌تونه شرکت کنه
    if exam.author_id == request.user.id:
        messages.warning(request, "شما نویسنده این آزمون هستید و نمی‌توانید در آزمون خودتان شرکت کنید.")
        return redirect('exams:detail', pk=pk)
    
    # بررسی شرکت قبلی
    existing_attempt = ExamAttempt.objects.filter(
        user=request.user, exam=exam, is_completed=True
    ).first()
    if existing_attempt:
        messages.info(request, "شما قبلاً در این آزمون شرکت کرده‌اید.")
        return redirect('exams:result', pk=exam.pk, attempt_id=existing_attempt.pk)
    
    pages = exam.pages.all()
    
    if not pages.exists():
        return redirect('exams:take', pk=pk)
    
    current_page = pages.filter(page_number=page_num).first()
    if not current_page:
        current_page = pages.first()
    
    total_pages = pages.count()
    is_last_page = current_page.page_number == pages.last().page_number
    next_page_num = current_page.page_number + 1
    prev_page_num = current_page.page_number - 1
    
    return render(request, 'exams/study.html', {
        'setting': setting,
        'exam': exam,
        'page': current_page,
        'total_pages': total_pages,
        'is_last_page': is_last_page,
        'next_page_num': next_page_num,
        'prev_page_num': prev_page_num,
        'active_page': 'exams',
    })


# ==========================================
# شرکت در آزمون (فقط یک بار، نه برای نویسنده)
# ==========================================
@login_required
def take_exam(request, pk):
    setting = SiteSetting.objects.first()
    if not request.user.is_approved:
        return redirect('accounts:login_step1')
    
    exam = get_object_or_404(Exam, pk=pk, is_approved=True)
    
    # نویسنده نمی‌تونه شرکت کنه
    if exam.author_id == request.user.id:
        messages.warning(request, "شما نویسنده این آزمون هستید و نمی‌توانید در آزمون خودتان شرکت کنید.")
        return redirect('exams:detail', pk=pk)
    
    # بررسی شرکت قبلی
    existing_attempt = ExamAttempt.objects.filter(
        user=request.user, exam=exam, is_completed=True
    ).first()
    if existing_attempt:
        messages.info(request, "شما قبلاً در این آزمون شرکت کرده‌اید و امکان شرکت مجدد وجود ندارد.")
        return redirect('exams:result', pk=exam.pk, attempt_id=existing_attempt.pk)
    
    questions = exam.questions.all()
    
    if not questions.exists():
        messages.warning(request, "این آزمون هنوز سوالی ندارد.")
        return redirect('exams:detail', pk=pk)
    
    if request.method == 'POST':
        # چک امنیتی دوباره در POST
        if exam.author_id == request.user.id:
            messages.error(request, "شما نمی‌توانید در آزمون خودتان شرکت کنید.")
            return redirect('exams:list')
        
        if ExamAttempt.objects.filter(user=request.user, exam=exam, is_completed=True).exists():
            messages.error(request, "شما قبلاً در این آزمون شرکت کرده‌اید.")
            return redirect('exams:list')
        
        exam_points = DIFFICULTY_POINTS.get(exam.difficulty, 1)
        
        attempt = ExamAttempt.objects.create(
            user=request.user,
            exam=exam,
            total_points=exam_points,
        )
        
        all_correct = True
        answered_count = 0
        total_questions = questions.count()
        
        for question in questions:
            selected = request.POST.get(f'question_{question.id}')
            
            if not selected:
                all_correct = False
                continue
            
            try:
                selected_int = int(selected)
                if selected_int not in [1, 2, 3, 4]:
                    all_correct = False
                    continue
            except (ValueError, TypeError):
                all_correct = False
                continue
            
            is_correct = (selected_int == question.correct_option)
            if not is_correct:
                all_correct = False
            
            UserAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected_int,
                is_correct=is_correct,
            )
            answered_count += 1
        
        # قانون همه یا هیچ
        is_perfect = all_correct and (answered_count == total_questions)
        
        if is_perfect:
            attempt.score = exam_points
            request.user.points = (request.user.points or 0) + exam_points
            request.user.save()
            messages.success(request, f"🎉 فوق‌العاده! شما تمام سوالات را درست پاسخ دادید و {exam_points} امتیاز گرفتید!")
        else:
            attempt.score = 0
            messages.info(request, "متأسفانه همه پاسخ‌ها درست نبود. طبق قانون آزمون، امتیازی تعلق نگرفت.")
        
        attempt.is_completed = True
        attempt.completed_at = timezone.now()
        attempt.save()
        
        return redirect('exams:result', pk=exam.pk, attempt_id=attempt.pk)
    
    return render(request, 'exams/take.html', {
        'setting': setting,
        'exam': exam,
        'questions': questions,
        'exam_points': DIFFICULTY_POINTS.get(exam.difficulty, 1),
        'active_page': 'exams',
    })


# ==========================================
# نتیجه آزمون
# ==========================================
@login_required
def exam_result(request, pk, attempt_id):
    setting = SiteSetting.objects.first()
    exam = get_object_or_404(Exam, pk=pk)
    attempt = get_object_or_404(ExamAttempt, pk=attempt_id, user=request.user, exam=exam)
    answers = attempt.answers.select_related('question').all()
    
    correct_count = answers.filter(is_correct=True).count()
    wrong_count = answers.filter(is_correct=False).count()
    total_count = exam.questions.count()
    unanswered = total_count - answers.count()
    
    is_perfect = (correct_count == total_count and wrong_count == 0 and unanswered == 0)
    exam_points = DIFFICULTY_POINTS.get(exam.difficulty, 1)
    
    return render(request, 'exams/result.html', {
        'setting': setting,
        'exam': exam,
        'attempt': attempt,
        'answers': answers,
        'correct_count': correct_count,
        'wrong_count': wrong_count,
        'unanswered': unanswered,
        'total_count': total_count,
        'is_perfect': is_perfect,
        'exam_points': exam_points,
        'active_page': 'exams',
    })


# ==========================================
# ساخت آزمون جدید
# ==========================================
@login_required
def create_exam(request):
    setting = SiteSetting.objects.first()
    if not request.user.is_approved:
        return redirect('accounts:login_step1')
    
    if request.method == 'POST':
        exam_form = ExamForm(request.POST)
        if exam_form.is_valid():
            exam = exam_form.save(commit=False)
            exam.author = request.user
            exam.is_approved = False
            exam.save()
            messages.success(request, "آزمون ساخته شد. حالا صفحات درس و سوالات را اضافه کنید.")
            return redirect('exams:manage_exam', pk=exam.pk)
    else:
        exam_form = ExamForm()
    
    return render(request, 'exams/create.html', {
        'setting': setting,
        'form': exam_form,
        'active_page': 'create',
    })


# ==========================================
# مدیریت آزمون
# ==========================================
@login_required
def manage_exam(request, pk):
    setting = SiteSetting.objects.first()
    if not request.user.is_approved:
        return redirect('accounts:login_step1')
    
    exam = get_object_or_404(Exam, pk=pk, author=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_page':
            page_form = ExamPageForm(request.POST)
            if page_form.is_valid():
                page = page_form.save(commit=False)
                page.exam = exam
                page.save()
                messages.success(request, "صفحه درس اضافه شد.")
                return redirect('exams:manage_exam', pk=pk)
            else:
                messages.error(request, "لطفاً اطلاعات صفحه را به درستی وارد کنید.")
        
        elif action == 'add_question':
            question_form = QuestionForm(request.POST)
            if question_form.is_valid():
                question = question_form.save(commit=False)
                question.exam = exam
                question.save()
                messages.success(request, "سوال اضافه شد.")
                return redirect('exams:manage_exam', pk=pk)
            else:
                messages.error(request, "لطفاً اطلاعات سوال را به درستی وارد کنید.")
        
        elif action == 'delete_page':
            page_id = request.POST.get('page_id')
            ExamPage.objects.filter(pk=page_id, exam=exam).delete()
            messages.success(request, "صفحه حذف شد.")
            return redirect('exams:manage_exam', pk=pk)
        
        elif action == 'delete_question':
            question_id = request.POST.get('question_id')
            Question.objects.filter(pk=question_id, exam=exam).delete()
            messages.success(request, "سوال حذف شد.")
            return redirect('exams:manage_exam', pk=pk)
        
        elif action == 'submit_for_approval':
            if exam.pages.exists() and exam.questions.exists():
                exam.is_approved = False
                exam.save()
                messages.success(request, "آزمون برای بررسی به ادمین ارسال شد.")
                return redirect('exams:my_exams')
            else:
                messages.error(request, "حداقل یک صفحه درس و یک سوال لازم است.")
    
    page_form = ExamPageForm()
    question_form = QuestionForm()
    
    return render(request, 'exams/manage.html', {
        'setting': setting,
        'exam': exam,
        'pages': exam.pages.all(),
        'questions': exam.questions.all(),
        'page_form': page_form,
        'question_form': question_form,
        'active_page': 'create',
    })


# ==========================================
# آزمون‌های من
# ==========================================
@login_required
def my_exams(request):
    setting = SiteSetting.objects.first()
    if not request.user.is_approved:
        return redirect('accounts:login_step1')
    
    exams = Exam.objects.filter(author=request.user).order_by('-created_at')
    
    return render(request, 'exams/my_exams.html', {
        'setting': setting,
        'exams': exams,
        'active_page': 'create',
    })