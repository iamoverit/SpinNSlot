import hashlib
import hmac
import time
from django.conf import settings
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import login, logout
from .forms import UserUpdateForm

from web.models import CustomUser

class TelegramLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            form = UserUpdateForm(instance=request.user)    
        else:
            # Для неаутентифицированных - пустую форму (или None)
            form = None
            messages.warning(request, 'Необходимо войти в систему')
        return render(request, 'telegram_login.html', {
            'form': form,
            'is_authenticated': request.user.is_authenticated
        })

class TelegramAuthView(View):
    def get(self, request):
        if request.method == "GET":
            data = request.GET
            data = request.GET.dict()
            auth_data = {k: v for k, v in data.items() if k != 'hash'}
            check_string = "\n".join(f"{k}={auth_data[k]}" for k in sorted(auth_data.keys()))
            secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
            computed_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()

            if computed_hash != data["hash"]:
                return render(request, "error.html", {"message": "Invalid Telegram authentication data."})

            if time.time() - int(auth_data["auth_date"]) > 10:
                return render(request, "error.html", {"message": "The login session has expired."})

            telegram_id = data.get("id")

            user, created = CustomUser.objects.get_or_create(telegram_id=telegram_id, 
                                                    defaults={
                                                        "username": data.get("username", telegram_id),
                                                        "first_name": data.get("first_name", ""),
                                                        "last_name": data.get("last_name", ""),
                                                        "avatar_url": data.get("photo_url")
                                                    })
            if not created:
                user.avatar_url = data.get("photo_url")
                user.save()
            login(request, user)
            return redirect('index')

class TelegramLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('index')