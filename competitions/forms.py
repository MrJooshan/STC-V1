# competitions/forms.py
from django import forms
from .models import Competition
import jdatetime
from .models import Competition, CompetitionQuestion

class CompetitionForm(forms.ModelForm):
    """فرم ساخت مسابقه با تاریخ شمسی"""
    
    jalali_date = forms.CharField(
        label="تاریخ شروع (شمسی)",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '1403/09/15',
            'pattern': r'\d{4}/\d{1,2}/\d{1,2}',
            'title': 'فرمت: 1403/09/15',
        }),
        help_text="مثال: 1403/09/15"
    )
    
    jalali_time = forms.CharField(
        label="ساعت شروع",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '18:30',
            'pattern': r'\d{1,2}:\d{2}',
            'title': 'فرمت: 18:30',
        }),
        help_text="مثال: 18:30"
    )
    
    class Meta:
        model = Competition
        fields = [
            'title', 'organizer', 'description', 'image',
            'duration_minutes', 'prize', 'has_certificate', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'عنوان مسابقه'}),
            'organizer': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'برگزارکننده'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'توضیحات مسابقه...'}),
            'image': forms.FileInput(attrs={'class': 'form-input'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'prize': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'مثلاً: ۵ میلیون تومان'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # اگه در حالت ویرایش بود، مقادیر شمسی رو پر کن
        if self.instance and self.instance.pk and self.instance.start_datetime:
            j = jdatetime.datetime.fromgregorian(datetime=self.instance.start_datetime)
            self.fields['jalali_date'].initial = j.strftime('%Y/%m/%d')
            self.fields['jalali_time'].initial = j.strftime('%H:%M')
    
    def clean(self):
        cleaned_data = super().clean()
        jalali_date_str = cleaned_data.get('jalali_date', '').strip()
        jalali_time_str = cleaned_data.get('jalali_time', '').strip()
        
        if not jalali_date_str or not jalali_time_str:
            raise forms.ValidationError('تاریخ و ساعت شروع الزامی است.')
        
        try:
            year, month, day = map(int, jalali_date_str.split('/'))
            hour, minute = map(int, jalali_time_str.split(':'))
            
            jalali_dt = jdatetime.datetime(year, month, day, hour, minute)
            gregorian_dt = jalali_dt.togregorian()
            
            from django.utils import timezone
            if timezone.is_naive(gregorian_dt):
                gregorian_dt = timezone.make_aware(gregorian_dt)
            
            cleaned_data['start_datetime'] = gregorian_dt
            
        except (ValueError, TypeError):
            raise forms.ValidationError('فرمت تاریخ یا ساعت نامعتبر است.')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.start_datetime = self.cleaned_data['start_datetime']
        if commit:
            instance.save()
        return instance
    






    from .models import Competition, CompetitionQuestion


class CompetitionQuestionForm(forms.ModelForm):
    class Meta:
        model = CompetitionQuestion
        fields = ['question_text', 'option_1', 'option_2', 'option_3', 'option_4', 'correct_option', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'متن سوال'}),
            'option_1': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'گزینه ۱'}),
            'option_2': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'گزینه ۲'}),
            'option_3': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'گزینه ۳'}),
            'option_4': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'گزینه ۴'}),
            'correct_option': forms.Select(attrs={'class': 'form-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
        }