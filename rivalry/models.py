from django.db import models
from accounts.models import CustomUser
from exams.models import Question


class RivalryMatch(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'در انتظار حریف'),
        ('playing', 'در حال بازی'),
        ('finished', 'پایان یافته'),
    ]
    
    player1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='matches_as_p1', verbose_name="بازیکن ۱")
    player2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='matches_as_p2', null=True, blank=True, verbose_name="بازیکن ۲")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting', verbose_name="وضعیت")
    winner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_matches', verbose_name="برنده")
    
    player1_score = models.IntegerField(default=0, verbose_name="امتیاز بازیکن ۱")
    player2_score = models.IntegerField(default=0, verbose_name="امتیاز بازیکن ۲")
    
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "مسابقه رقابتی"
        verbose_name_plural = "مسابقات رقابتی"

    def __str__(self):
        return f"{self.player1.display_name} vs {self.player2.display_name if self.player2 else '?'}"


class RivalryQuestion(models.Model):
    match = models.ForeignKey(RivalryMatch, on_delete=models.CASCADE, related_name='questions', verbose_name="مسابقه")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="سوال")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    
    answered_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='answered_rivalry_questions', verbose_name="پاسخ داده شده توسط")
    is_correct = models.BooleanField(null=True, blank=True, verbose_name="صحیح بوده؟")

    class Meta:
        verbose_name = "سوال رقابتی"
        verbose_name_plural = "سوالات رقابتی"
        ordering = ['order']