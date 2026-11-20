# exams/admin.py
from django.contrib import admin
from .models import Category, Exam, ExamPage, Question, ExamAttempt, UserAnswer


class ExamPageInline(admin.TabularInline):
    model = ExamPage
    extra = 1
    fields = ('page_number', 'title', 'content')


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('order', 'question_text', 'option_1', 'option_2', 'option_3', 'option_4', 'correct_option', 'points')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'total_questions', 'time_limit', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'category', 'difficulty', 'created_at')
    search_fields = ('title', 'description', 'author__phone_number')
    list_editable = ('is_approved',)
    inlines = [ExamPageInline, QuestionInline]
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'description', 'category', 'author', 'time_limit', 'difficulty')
        }),
        ('وضعیت', {
            'fields': ('is_approved',),
            'description': 'تیک تایید را بزنید تا آزمون برای کاربران نمایش داده شود.'
        }),
    )


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'score', 'total_points', 'is_completed', 'started_at')
    list_filter = ('is_completed', 'exam', 'started_at')
    search_fields = ('user__phone_number', 'exam__title')
    readonly_fields = ('user', 'exam', 'score', 'total_points', 'is_completed', 'started_at', 'completed_at')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'question_text', 'correct_option', 'points')
    list_filter = ('exam',)
    search_fields = ('question_text',)
