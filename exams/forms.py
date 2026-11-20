# exams/forms.py
from django import forms
from .models import Exam, ExamPage, Question, Category


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'description', 'category', 'time_limit', 'difficulty']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'عنوان آزمون', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'placeholder': 'توضیحات کوتاه', 'rows': 3, 'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'time_limit': forms.NumberInput(attrs={'placeholder': 'مدت زمان (دقیقه)', 'min': 1, 'class': 'form-input'}),
            'difficulty': forms.Select(attrs={'class': 'form-input'}),
        }


class ExamPageForm(forms.ModelForm):
    class Meta:
        model = ExamPage
        fields = ['page_number', 'title', 'content']
        widgets = {
            'page_number': forms.NumberInput(attrs={'min': 1, 'class': 'form-input'}),
            'title': forms.TextInput(attrs={'placeholder': 'عنوان صفحه (اختیاری)', 'class': 'form-input'}),
            'content': forms.Textarea(attrs={'placeholder': 'متن درس این صفحه را وارد کنید...', 'rows': 8, 'class': 'form-input'}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'option_1', 'option_2', 'option_3', 'option_4', 'correct_option', 'points', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={'placeholder': 'متن سوال', 'rows': 2, 'class': 'form-input'}),
            'option_1': forms.TextInput(attrs={'placeholder': 'گزینه ۱', 'class': 'form-input'}),
            'option_2': forms.TextInput(attrs={'placeholder': 'گزینه ۲', 'class': 'form-input'}),
            'option_3': forms.TextInput(attrs={'placeholder': 'گزینه ۳', 'class': 'form-input'}),
            'option_4': forms.TextInput(attrs={'placeholder': 'گزینه ۴', 'class': 'form-input'}),
            'correct_option': forms.Select(attrs={'class': 'form-input'}),
            'points': forms.NumberInput(attrs={'min': 1, 'class': 'form-input'}),
            'order': forms.NumberInput(attrs={'min': 0, 'class': 'form-input'}),
        }