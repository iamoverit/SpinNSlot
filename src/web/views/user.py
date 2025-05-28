from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import UserUpdateForm
from django.http import JsonResponse

@login_required(login_url='telegram_login')
def user_update(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные успешно обновлены!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'telegram_login.html', {'form': form})

def set_theme(request):
    if request.method == 'POST':
        theme = request.POST.get('theme', 'light')
        request.session['theme'] = theme
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)