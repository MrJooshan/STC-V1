# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('وارد کردن شماره موبایل الزامی است')
        
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_approved', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)


class CustomUser(AbstractUser):
    # غیرفعال کردن username
    username = None
    
    phone_number = models.CharField(
        max_length=11, 
        unique=True, 
        validators=[RegexValidator(regex=r'^09\d{9}$', message="شماره موبایل نامعتبر است.")],
        verbose_name="شماره موبایل"
    )
    
    student_id = models.CharField(max_length=20, blank=True, null=True, verbose_name="کد دانشجویی")
    university_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="نام دانشگاه")
    field_of_study = models.CharField(max_length=100, blank=True, null=True, verbose_name="رشته تحصیلی")
    
    is_approved = models.BooleanField(default=False, verbose_name="تایید شده توسط ادمین")
    otp_code = models.CharField(max_length=6, blank=True, null=True, verbose_name="کد تایید")
    
    points = models.IntegerField(default=0, verbose_name="امتیاز کل")
    level = models.IntegerField(default=1, verbose_name="سطح کاربر")
    success_rate = models.IntegerField(default=0, verbose_name="درصد موفقیت")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="عکس پروفایل")
    
    # 👇 فیلدهای جدید برای سیستم رقابت 👇
    rivalry_wins = models.IntegerField(default=0, verbose_name="تعداد بردها در رقابت")
    rivalry_losses = models.IntegerField(default=0, verbose_name="تعداد باخت‌ها در رقابت")

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone_number}"
    
    @property
    def display_name(self):
        full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return full_name if full_name else self.phone_number
    
    @property
    def initial(self):
        if self.first_name:
            return self.first_name[0]
        return self.phone_number[0] if self.phone_number else "؟"


class SiteSetting(models.Model):
    logo = models.ImageField(upload_to='site/', verbose_name="لوگوی اصلی (وسط)")
    flag_image = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name="عکس پرچم (گوشه چپ)")
    site_title = models.CharField(max_length=100, default="مسیرم معلم", verbose_name="عنوان سایت")
    background_image = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name="عکس پس‌زمینه")

    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"

    def __str__(self):
        return "تنظیمات ظاهری"


# ==========================================
# مدل‌های تیکت و پشتیبانی
# ==========================================
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'باز'),
        ('answered', 'پاسخ داده شده'),
        ('closed', 'بسته شده'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tickets', verbose_name="کاربر")
    subject = models.CharField(max_length=200, verbose_name="موضوع تیکت")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name="وضعیت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")
    
    class Meta:
        verbose_name = "تیکت"
        verbose_name_plural = "تیکت‌ها"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.subject} - {self.user.display_name}"
    
    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()
    
    @property
    def unread_for_admin(self):
        last = self.last_message
        return last and last.sender_type == 'user'


class TicketMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'کاربر'),
        ('admin', 'مدیر'),
    ]
    
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages', verbose_name="تیکت")
    sender_type = models.CharField(max_length=10, choices=SENDER_CHOICES, verbose_name="نوع فرستنده")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="فرستنده")
    message = models.TextField(verbose_name="متن پیام")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")
    
    class Meta:
        verbose_name = "پیام تیکت"
        verbose_name_plural = "پیام‌های تیکت"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.ticket.subject} - {self.sender_type}"
