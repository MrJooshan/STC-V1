# competitions/admin.py
from django.contrib import admin
from .models import Competition


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'jalali_full', 'status_display', 'is_active', 'has_certificate')
    list_filter = ('is_active', 'has_certificate')
    search_fields = ('title', 'organizer', 'description')
    readonly_fields = ('created_at', 'created_by')
from .models import Competition, CompetitionQuestion, CompetitionAttempt, CompetitionAnswer


class CompetitionQuestionInline(admin.TabularInline):
    model = CompetitionQuestion
    extra = 1
    fields = ('order', 'question_text', 'option_1', 'option_2', 'option_3', 'option_4', 'correct_option')


# این خط رو به CompetitionAdmin اضافه کن:
# inlines = [CompetitionQuestionInline]


@admin.register(CompetitionAttempt)
class CompetitionAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'competition', 'score', 'total_points', 'is_completed', 'started_at')
    list_filter = ('is_completed', 'competition')
    search_fields = ('user__phone_number', 'competition__title')