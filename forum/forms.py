# forum/forms.py
from django import forms
from .models import ForumPost, ForumComment


class ForumPostForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'عنوان (اختیاری)', 'class': 'form-input'}),
            'content': forms.Textarea(attrs={'placeholder': 'چه چیزی توی ذهنته؟ بنویس...', 'rows': 5, 'class': 'form-input'}),
        }


class ForumCommentForm(forms.ModelForm):
    class Meta:
        model = ForumComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'نظرت رو بنویس...', 'rows': 2, 'class': 'form-input'}),
        }