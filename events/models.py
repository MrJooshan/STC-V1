from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان خبر")
    content = models.TextField(verbose_name="متن خبر")
    image = models.ImageField(upload_to='events/', verbose_name="عکس خبر")
    is_active = models.BooleanField(default=True, verbose_name="فعال (نمایش در سایت)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ انتشار")

    class Meta:
        verbose_name = "رویداد"
        verbose_name_plural = "رویدادها"
        ordering = ['-created_at']

    def __str__(self):
        return self.title
