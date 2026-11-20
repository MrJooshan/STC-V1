# accounts/forms.py
from django import forms
from django.core.validators import RegexValidator


class PhoneForm(forms.Form):
    phone_number = forms.CharField(
        max_length=11, min_length=11,
        validators=[RegexValidator(regex=r'^09\d{9}$', message="شماره موبایل نامعتبر است.")],
        widget=forms.TextInput(attrs={
            'placeholder': 'شماره موبایل (مثلا 09123456789)',
            'inputmode': 'numeric',
            'pattern': '09[0-9]{9}',
            'maxlength': '11'
        })
    )


class OTPForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6, min_length=6,
        validators=[RegexValidator(regex=r'^\d{6}$', message="کد باید ۶ رقم باشد.")],
        widget=forms.TextInput(attrs={
            'placeholder': 'کد ۶ رقمی پیامک شده',
            'inputmode': 'numeric',
            'pattern': '[0-9]{6}',
            'maxlength': '6'
        })
    )


class ProfileCompletionForm(forms.Form):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'نام'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'نام خانوادگی'}))
    student_id = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': 'کد دانشجویی'}))
    university_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'نام دانشگاه'}))
    field_of_study = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'رشته تحصیلی'}))
    
    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور (حداقل ۶ کاراکتر)'})
    )
    password_confirm = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={'placeholder': 'تکرار رمز عبور'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get('password')
        pwc = cleaned_data.get('password_confirm')
        if pw and pwc and pw != pwc:
            raise forms.ValidationError('رمز عبور و تکرار آن یکسان نیستند.')
        return cleaned_data


class PasswordLoginForm(forms.Form):
    phone_number = forms.CharField(
        max_length=11, min_length=11,
        validators=[RegexValidator(regex=r'^09\d{9}$', message="شماره موبایل نامعتبر است.")],
        widget=forms.TextInput(attrs={
            'placeholder': 'شماره موبایل',
            'inputmode': 'numeric',
            'pattern': '09[0-9]{9}',
            'maxlength': '11'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور'})
    )


# 👇 این کلاس قبلاً به اشتباه داخل PasswordLoginForm بود، حالا جداست 👇
class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور جدید (حداقل ۶ کاراکتر)'})
    )
    confirm_password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={'placeholder': 'تکرار رمز عبور جدید'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get('new_password')
        pwc = cleaned_data.get('confirm_password')
        if pw and pwc and pw != pwc:
            raise forms.ValidationError('رمز عبور و تکرار آن یکسان نیستند.')
        return cleaned_data


class TicketForm(forms.Form):
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'موضوع تیکت', 'class': 'form-input'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'پیام خود را بنویسید...', 'rows': 5, 'class': 'form-input'})
    )


class TicketReplyForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'پاسخ خود را بنویسید...', 'rows': 3, 'class': 'form-input'})
    )