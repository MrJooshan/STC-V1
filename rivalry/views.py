from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import SiteSetting


@login_required
def lobby(request):
    setting = SiteSetting.objects.first()
    return render(request, 'rivalry/lobby.html', {
        'setting': setting,
    })
