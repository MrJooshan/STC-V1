# exams/models.py
from django.db import models
from django.urls import reverse
from accounts.models import CustomUser


class Category(models.Model):
    """دسته‌بندی موضوعی آزمون‌ها (توسط ادمین ساخته میشه)"""
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="آیکون")
    color = models.CharField(max_length=20, default="#f1c40f", verbose_name="رنگ (کد HEX)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.name


class Exam(models.Model):
    """آزمون (شامل متن درس + سوالات چهارگزینه‌ای)"""
    DIFFICULTY_CHOICES = [
        ('easy', 'آسان'),
        ('medium', 'متوسط'),
        ('hard', 'سخت'),
    ]

    title = models.CharField(max_length=200, verbose_name="عنوان آزمون")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='exams', verbose_name="دسته‌بندی")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                related_name='created_exams', verbose_name="سازنده")
    time_limit = models.PositiveIntegerField(default=10, verbose_name="مدت زمان (دقیقه)")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium', verbose_name="سطح")
    is_approved = models.BooleanField(default=False, verbose_name="تایید ادمین")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "آزمون"
        verbose_name_plural = "آزمون‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('exams:detail', args=[self.pk])

    @property
    def total_questions(self):
        return self.questions.count()

    @property
    def total_pages(self):
        return self.pages.count()


class ExamPage(models.Model):
    """صفحات متن درس (برای آزمون‌های چند صفحه‌ای)"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='pages', verbose_name="آزمون")
    page_number = models.PositiveIntegerField(verbose_name="شماره صفحه")
    title = models.CharField(max_length=200, blank=True, null=True, verbose_name="عنوان صفحه")
    content = models.TextField(verbose_name="متن صفحه")

    class Meta:
        verbose_name = "صفحه درس"
        verbose_name_plural = "صفحات درس"
        ordering = ['page_number']

    def __str__(self):
        return f"{self.exam.title} - صفحه {self.page_number}"


class Question(models.Model):
    """سوالات چهارگزینه‌ای"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions', verbose_name="آزمون")
    question_text = models.TextField(verbose_name="متن سوال")
    option_1 = models.CharField(max_length=300, verbose_name="گزینه ۱")
    option_2 = models.CharField(max_length=300, verbose_name="گزینه ۲")
    option_3 = models.CharField(max_length=300, verbose_name="گزینه ۳")
    option_4 = models.CharField(max_length=300, verbose_name="گزینه ۴")
    correct_option = models.PositiveSmallIntegerField(
        choices=[(1, 'گزینه ۱'), (2, 'گزینه ۲'), (3, 'گزینه ۳'), (4, 'گزینه ۴')],
        verbose_name="گزینه صحیح"
    )
    points = models.PositiveSmallIntegerField(default=1, verbose_name="بارم")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "سوال"
        verbose_name_plural = "سوالات"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.exam.title} - {self.question_text[:40]}"

    def get_options(self):
        return [(1, self.option_1), (2, self.option_2), (3, self.option_3), (4, self.option_4)]


class ExamAttempt(models.Model):
    """تلاش کاربر در آزمون"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                              related_name='attempts', verbose_name="کاربر")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE,
                              related_name='attempts', verbose_name="آزمون")
    score = models.FloatField(default=0, verbose_name="امتیاز کسب شده")
    total_points = models.PositiveIntegerField(default=0, verbose_name="کل بارم")
    is_completed = models.BooleanField(default=False, verbose_name="تکمیل شده")
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان شروع")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان اتمام")

    class Meta:
        verbose_name = "تلاش آزمون"
        verbose_name_plural = "تلاش‌های آزمون"
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.phone_number} - {self.exam.title}"

    @property
    def score_percent(self):
        if self.total_points > 0:
            return round((self.score / self.total_points) * 100)
        return 0


class UserAnswer(models.Model):
    """پاسخ کاربر به هر سوال"""
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE,
                                  related_name='answers', verbose_name="تلاش")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="سوال")
    selected_option = models.PositiveSmallIntegerField(verbose_name="گزینه انتخاب شده")
    is_correct = models.BooleanField(default=False, verbose_name="صحیح است")

    class Meta:
        verbose_name = "پاسخ کاربر"
        verbose_name_plural = "پاسخ‌های کاربر"

    def __str__(self):
        return f"{self.attempt} - Q{self.question.id}"
