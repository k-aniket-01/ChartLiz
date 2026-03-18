from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ProfileForm
from django.http import JsonResponse
import json 

# Create your views here.
@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect(profile)
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'users/profile.html', {'form':form})

@login_required
def toggle_dark_mode(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request.user.dark_mode =  data.get('dark_mode', False)
        request.user.save()
        return JsonResponse({"status":'ok'})
    
