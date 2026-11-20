# forum/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from accounts.models import SiteSetting, CustomUser
from .models import ForumPost, ForumComment
from .forms import ForumPostForm, ForumCommentForm
from .utils import validate_content, is_rate_limited


@login_required
def forum_list(request):
    setting = SiteSetting.objects.first()
    if not request.user.is_approved:
        return redirect('accounts:login_step1')
    
    posts = ForumPost.objects.filter(is_approved=True).select_related('author').prefetch_related('likes', 'comments')
    
    return render(request, 'forum/list.html', {
        'setting': setting,
        'posts': posts,
        'active_page': 'forum',
    })


@login_required
def create_post(request):
    setting = SiteSetting.objects.first()
    if not request.user.is_approved:
        return redirect('accounts:login_step1')
    
    if request.method == 'POST':
        form = ForumPostForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            
            if is_rate_limited(request.user, 'post'):
                messages.error(request, "شما اخیراً نوشته‌های زیادی ارسال کرده‌اید. لطفاً کمی صبر کنید.")
                return redirect('forum:create')
            
            is_valid, error = validate_content(content)
            if not is_valid:
                messages.error(request, error)
                return redirect('forum:create')
            
            post = form.save(commit=False)
            post.author = request.user
            post.is_approved = False
            post.save()
            
            messages.success(request, "✓ نوشته شما ثبت شد و پس از تایید ادمین نمایش داده خواهد شد.")
            return redirect('forum:list')
    else:
        form = ForumPostForm()
    
    return render(request, 'forum/create.html', {
        'setting': setting,
        'form': form,
        'active_page': 'forum',
    })


@login_required
def post_detail(request, pk):
    setting = SiteSetting.objects.first()
    if not request.user.is_approved:
        return redirect('accounts:login_step1')
    
    post = get_object_or_404(ForumPost, pk=pk, is_approved=True)
    comments = post.comments.filter(parent__isnull=True, is_approved=True).select_related('author').prefetch_related('replies__author', 'replies__likes', 'likes')
    
    if request.method == 'POST':
        form = ForumCommentForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            
            if is_rate_limited(request.user, 'comment'):
                messages.error(request, "شما اخیراً نظرات زیادی ارسال کرده‌اید. لطفاً کمی صبر کنید.")
                return redirect('forum:detail', pk=pk)
            
            is_valid, error = validate_content(content)
            if not is_valid:
                messages.error(request, error)
                return redirect('forum:detail', pk=pk)
            
            parent_id = request.POST.get('parent_id')
            parent = None
            if parent_id:
                try:
                    parent = ForumComment.objects.get(pk=parent_id, post=post)
                except ForumComment.DoesNotExist:
                    pass
            
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.parent = parent
            comment.is_approved = True
            comment.save()
            
            messages.success(request, "✓ نظر شما ثبت شد.")
            return redirect('forum:detail', pk=pk)
    else:
        form = ForumCommentForm()
    
    return render(request, 'forum/detail.html', {
        'setting': setting,
        'post': post,
        'comments': comments,
        'form': form,
        'active_page': 'forum',
    })


@login_required
@require_POST
def like_post(request, pk):
    post = get_object_or_404(ForumPost, pk=pk)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({'liked': liked, 'total': post.total_likes})


@login_required
@require_POST
def like_comment(request, pk):
    comment = get_object_or_404(ForumComment, pk=pk)
    
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    
    return JsonResponse({'liked': liked, 'total': comment.total_likes})


@login_required
def user_info(request, user_id):
    """API برای مودال اطلاعات کاربر"""
    user = get_object_or_404(CustomUser, pk=user_id)
    return JsonResponse({
        'first_name': user.first_name or '',
        'last_name': user.last_name or '',
        'phone': user.phone_number,
        'university': user.university_name or 'دانشگاه فرهنگیان',
        'field': user.field_of_study or '',
        'level': user.level or 1,
        'points': user.points or 0,
        'avatar': user.avatar.url if user.avatar else None,
        'initial': (user.first_name[:1] if user.first_name else user.phone_number[:1]),
    })
