# forum/utils.py
import re
from datetime import timedelta
from django.utils import timezone
from .models import ForumPost, ForumComment

# ==========================================
# 👇 لیست کلمات نامناسب - خودت اضافه کن 👇
# ==========================================
BAD_WORDS = [
    'کلمه_بد1', 'کلمه_بد2', 'فحش1', 'فحش2',
    # کلمات واقعی رو اینجا اضافه کن
]

SPAM_PATTERNS = [
    r'https?://',   # لینک
    r'www\.',       # لینک
    r'@\w+',        # منشن تلگرام
    r't\.me',       # تلگرام
    r'bit\.ly',     # لینک کوتاه
]


def contains_bad_words(text):
    """بررسی کلمات نامناسب"""
    text_lower = text.lower()
    for word in BAD_WORDS:
        if word in text_lower:
            return True
    return False


def contains_spam(text):
    """تشخیص اسپم"""
    url_count = 0
    for pattern in SPAM_PATTERNS:
        url_count += len(re.findall(pattern, text, re.IGNORECASE))
    
    # اگه بیش از ۱ لینک داشت
    if url_count >= 2:
        return True
    
    # تکرار بیش از حد یه کاراکتر (۱۰ بار)
    if re.search(r'(.)\1{9,}', text):
        return True
    
    # تکرار بیش از حد کل متن
    if len(text) > 50 and len(set(text)) < 8:
        return True
    
    return False


def is_rate_limited(user, action='post'):
    """محدودیت تعداد ارسال در بازه زمانی"""
    now = timezone.now()
    
    if action == 'post':
        recent = ForumPost.objects.filter(
            author=user,
            created_at__gte=now - timedelta(minutes=5)
        ).count()
        return recent >= 3  # حداکثر ۳ پست در ۵ دقیقه
    
    elif action == 'comment':
        recent = ForumComment.objects.filter(
            author=user,
            created_at__gte=now - timedelta(minutes=2)
        ).count()
        return recent >= 5  # حداکثر ۵ کامنت در ۲ دقیقه
    
    return False


def validate_content(text):
    """اعتبارسنجی کامل متن"""
    if len(text.strip()) < 3:
        return False, "متن شما خیلی کوتاه است (حداقل ۳ کاراکتر)."
    
    if len(text) > 2000:
        return False, "متن شما خیلی طولانی است (حداکثر ۲۰۰۰ کاراکتر)."
    
    if contains_bad_words(text):
        return False, "متن شما شامل کلمات نامناسب است. لطفاً ادب را رعایت کنید."
    
    if contains_spam(text):
        return False, "متن شما به عنوان اسپم تشخیص داده شد. از ارسال لینک‌های متعدد خودداری کنید."
    
    return True, None