# forum/models.py
from django.db import models
from accounts.models import CustomUser


class ForumPost(models.Model):
    """نوشته اصلی انجمن (نیاز به تایید ادمین)"""
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='forum_posts', verbose_name="نویسنده")
    title = models.CharField(max_length=200, blank=True, null=True, verbose_name="عنوان")
    content = models.TextField(verbose_name="متن نوشته")
    is_approved = models.BooleanField(default=False, verbose_name="تایید شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    likes = models.ManyToManyField(CustomUser, related_name='liked_forum_posts', blank=True, verbose_name="لایک‌ها")

    class Meta:
        verbose_name = "نوشته انجمن"
        verbose_name_plural = "نوشته‌های انجمن"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.phone_number} - {self.content[:40]}"

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def total_comments(self):
        return self.comments.filter(parent__isnull=True, is_approved=True).count()


class ForumComment(models.Model):
    """نظر/پاسخ (بدون نیاز به تایید ادمین)"""
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments', verbose_name="نوشته")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='forum_comments', verbose_name="نویسنده")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', verbose_name="پاسخ به")
    content = models.TextField(verbose_name="متن نظر")
    is_approved = models.BooleanField(default=True, verbose_name="تایید شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    likes = models.ManyToManyField(CustomUser, related_name='liked_forum_comments', blank=True, verbose_name="لایک‌ها")

    class Meta:
        verbose_name = "نظر انجمن"
        verbose_name_plural = "نظرات انجمن"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.phone_number} - {self.content[:40]}"

    @property
    def total_likes(self):
        return self.likes.count()