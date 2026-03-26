from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.paginator import Paginator
import json
from .forms import AlertForm
from .models import Alert, Notification


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



@login_required
def notification_center(request):
    notifs   = Notification.objects.filter(user=request.user)
    unread = notifs.filter(is_read=False).count
    paginator = Paginator(notifs, 20)
    page_obj  = paginator.get_page(request.GET.get('page'))
    unread    = notifs.filter(is_read=False).count()

    notifs.filter(is_read=False).update(is_read=True)

    return render(request, 'alerts/notification_center.html', {
        'page_obj': page_obj,
        'unread':   unread,
    })

@login_required
@require_POST
def mark_read(request, pk):
    Notification.objects.filter(pk=pk, user=request.user).update(is_read=True)
    return JsonResponse({'ok':True})

@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'ok':True})

@login_required
def recent_notifications(request):
    notifs = Notification.objects.filter(user=request.user)[:5]
    unread = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({
        'unread_count':unread,
        'notifications':[{
            'id':n.id,
            'title':n.title,
            'body':n.body,
            'is_read':n.is_read,
    }for n in notifs]
    })