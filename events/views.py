from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import SiteSetting
from .models import Event

@login_required
def event_list(request):
    setting = SiteSetting.objects.first()
    events = Event.objects.filter(is_active=True)
    return render(request, 'events/list.html', {
        'setting': setting,
        'events': events,
    })

@login_required
def event_detail(request, pk):
    setting = SiteSetting.objects.first()
    event = get_object_or_404(Event, pk=pk, is_active=True)
    return render(request, 'events/detail.html', {
        'setting': setting,
        'event': event,
    })