from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from .forms import AlertForm
from .models import Alert


@login_required
def alert_list(request):
    alerts = Alert.objects.filter(user=request.user)
    form   = AlertForm()
    return render(request, 'alerts/alert_list.html', {
        'alerts': alerts,
        'form':   form,
    })


@login_required
@require_POST
def alert_create(request):
    form = AlertForm(request.POST)
    if form.is_valid():
        alert        = form.save(commit=False)
        alert.user   = request.user
        alert.symbol = alert.symbol.upper()  # always store uppercase
        alert.save()
        messages.success(request, f'Alert created for {alert.symbol}.')
    else:
        messages.error(request, 'Check the form — something is missing.')
    return redirect('alerts:alert_list')


@login_required
@require_POST
def alert_delete(request, pk):
    alert = Alert.objects.filter(pk=pk, user=request.user).first()
    if alert:
        alert.delete()
        messages.success(request, 'Alert deleted.')
    return redirect('alerts:alert_list')