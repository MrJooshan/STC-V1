# competitions/models.py
from django.db import models
from accounts.models import CustomUser
import jdatetime


class Competition(models.Model):
    """مسابقات (فقط ادمین می‌سازد)"""
    
    title = models.CharField(max_length=200, verbose_name="عنوان مسابقه")
    organizer = models.CharField(
        max_length=200, 
        verbose_name="برگزارکننده / نهاد",
        help_text="مثلاً: دانشگاه فرهنگیان، سازمان بسیج، ..."
    )
    description = models.TextField(verbose_name="توضیحات")
    image = models.ImageField(upload_to='competitions/', verbose_name="عکس مسابقه")
    
    start_datetime = models.DateTimeField(verbose_name="تاریخ و ساعت شروع")
    duration_minutes = models.PositiveIntegerField(
        default=60, 
        verbose_name="مدت زمان (دقیقه)",
        help_text="مسابقه به مدت چند دقیقه فعال است؟"
    )
    
    prize = models.CharField(
        max_length=300, 
        blank=True, 
        null=True, 
        verbose_name="جایزه",
        help_text="مثلاً: ۵ میلیون تومان، کارت هدیه، ..."
    )
    has_certificate = models.BooleanField(default=False, verbose_name="گواهی دارد؟")
    
    is_active = models.BooleanField(default=True, verbose_name="فعال (نمایش در صفحه اصلی)")
    created_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_competitions',
        verbose_name="ساخته شده توسط"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ساخت")

    class Meta:
        verbose_name = "مسابقه"
        verbose_name_plural = "مسابقات"
        ordering = ['start_datetime']

    def __str__(self):
        return self.title

    # ==========================================
    # وضعیت مسابقه
    # ==========================================
    @property
    def status(self):
        """وضعیت فعلی: upcoming / live / finished"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        if now < self.start_datetime:
            return 'upcoming'
        end_time = self.start_datetime + timedelta(minutes=self.duration_minutes)
        if now <= end_time:
            return 'live'
        return 'finished'

    @property
    def status_display(self):
        return {
            'upcoming': 'شروع نشده',
            'live': 'در حال برگزاری',
            'finished': 'پایان یافته',
        }.get(self.status, '')

    @property
    def status_color(self):
        return {
            'upcoming': '#3498db',
            'live': '#e74c3c',
            'finished': '#7f8c8d',
        }.get(self.status, '#3498db')

    # ==========================================
    # نمایش تاریخ به شمسی
    # ==========================================
    @property
    def jalali_date(self):
        return jdatetime.datetime.fromgregorian(datetime=self.start_datetime).strftime('%Y/%m/%d')

    @property
    def jalali_time(self):
        return jdatetime.datetime.fromgregorian(datetime=self.start_datetime).strftime('%H:%M')

    @property
    def jalali_full(self):
        j = jdatetime.datetime.fromgregorian(datetime=self.start_datetime)
        return j.strftime('%A %d %B %Y - %H:%M')

    @property
    def countdown_seconds(self):
        """چند ثانیه تا شروع مونده"""
        from django.utils import timezone
        diff = (self.start_datetime - timezone.now()).total_seconds()
        return max(0, int(diff))


# ==========================================
# سوالات مسابقه (چهارگزینه‌ای)
# ==========================================
class CompetitionQuestion(models.Model):
    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE, 
        related_name='questions', verbose_name="مسابقه"
    )
    question_text = models.TextField(verbose_name="متن سوال")
    option_1 = models.CharField(max_length=300, verbose_name="گزینه ۱")
    option_2 = models.CharField(max_length=300, verbose_name="گزینه ۲")
    option_3 = models.CharField(max_length=300, verbose_name="گزینه ۳")
    option_4 = models.CharField(max_length=300, verbose_name="گزینه ۴")
    correct_option = models.PositiveSmallIntegerField(
        choices=[(1,'گزینه ۱'),(2,'گزینه ۲'),(3,'گزینه ۳'),(4,'گزینه ۴')],
        verbose_name="گزینه صحیح"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "سوال مسابقه"
        verbose_name_plural = "سوالات مسابقه"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.competition.title} - {self.question_text[:40]}"

    def get_options(self):
        return [(1, self.option_1), (2, self.option_2), (3, self.option_3), (4, self.option_4)]


# ==========================================
# شرکت کاربران در مسابقه
# ==========================================
class CompetitionAttempt(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='competition_attempts', verbose_name="کاربر"
    )
    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE,
        related_name='attempts', verbose_name="مسابقه"
    )
    score = models.FloatField(default=0, verbose_name="امتیاز")
    total_points = models.PositiveIntegerField(default=0, verbose_name="کل بارم")
    is_completed = models.BooleanField(default=False, verbose_name="تکمیل شده")
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="شروع")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="اتمام")

    class Meta:
        verbose_name = "شرکت در مسابقه"
        verbose_name_plural = "شرکت‌ها در مسابقه"
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.display_name} - {self.competition.title}"

    @property
    def score_percent(self):
        if self.total_points > 0:
            return round((self.score / self.total_points) * 100)
        return 0


class CompetitionAnswer(models.Model):
    attempt = models.ForeignKey(
        CompetitionAttempt, on_delete=models.CASCADE,
        related_name='answers', verbose_name="شرکت"
    )
    question = models.ForeignKey(CompetitionQuestion, on_delete=models.CASCADE, verbose_name="سوال")
    selected_option = models.PositiveSmallIntegerField(verbose_name="گزینه")
    is_correct = models.BooleanField(default=False, verbose_name="صحیح")

    class Meta:
        verbose_name = "پاسخ مسابقه"
        verbose_name_plural = "پاسخ‌های مسابقه"