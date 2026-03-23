import json
import secrets
import string

import requests
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_POST

from web.models import CustomUser

User = get_user_model()


def _generate_code_verifier(length: int = 64) -> str:
    alphabet = string.ascii_letters + string.digits + "-_"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _generate_state(length: int = 48) -> str:
    alphabet = string.ascii_letters + string.digits + "-_"
    return "".join(secrets.choice(alphabet) for _ in range(length))


@require_GET
def vk_pkce(request):
    code_verifier = _generate_code_verifier()
    state = _generate_state()

    # Сохраняем ожидаемые значения в серверной сессии
    request.session["vk_code_verifier"] = code_verifier
    request.session["vk_state"] = state

    return JsonResponse({
        "app_id": settings.VK_CLIENT_ID,
        "redirect_uri": settings.VK_REDIRECT_URI,
        "code_verifier": code_verifier,
        "state": state,
    })


@csrf_protect
def vk_callback(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    code = data.get("code")
    device_id = data.get("device_id")
    state = data.get("state")
    code_verifier = data.get("code_verifier")

    saved_state = request.session.get("vk_state")
    saved_code_verifier = request.session.get("vk_code_verifier")

    if not code:
        return JsonResponse({"ok": False, "error": "missing_code"}, status=400)

    if not device_id:
        return JsonResponse({"ok": False, "error": "missing_device_id"}, status=400)

    if not state or state != saved_state:
        return JsonResponse({"ok": False, "error": "invalid_state"}, status=400)

    if not code_verifier or code_verifier != saved_code_verifier:
        return JsonResponse({"ok": False, "error": "invalid_code_verifier"}, status=400)

    token_resp = requests.post(
        "https://id.vk.ru/oauth2/auth",
        data={
            "grant_type": "authorization_code",
            "code_verifier": code_verifier,
            "redirect_uri": settings.VK_REDIRECT_URI,
            "code": code,
            "client_id": settings.VK_CLIENT_ID,
            "client_secret": settings.VK_CLIENT_SECRET,
            "device_id": device_id,
            "state": state,
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=15,
    )

    token_data = token_resp.json()
    access_token = token_data.get("access_token")
    if not access_token:
        return JsonResponse(
            {"ok": False, "error": "missing_access_token", "details": token_data},
            status=400,
        )

    user_info_resp = requests.post(
        "https://id.vk.ru/oauth2/user_info",
        data={
            "client_id": settings.VK_CLIENT_ID,
            "access_token": access_token,
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=15,
    )

    user_info_data = user_info_resp.json()

    vk_user = user_info_data.get("user") or {}
    vk_user_id = vk_user.get("user_id")

    if not vk_user_id:
        return JsonResponse(
            {"ok": False, "error": "missing_vk_user_id", "details": user_info_data},
            status=400,
        )

    first_name = vk_user.get("first_name", "")
    last_name = vk_user.get("last_name", "")
    email = vk_user.get("email", "")
    phone = vk_user.get("phone", "")
    avatar = vk_user.get("avatar", "")

    user, created = CustomUser.objects.get_or_create(
        vk_id=f"vk_{vk_user_id}",
        defaults={
            "username": f"vk_{vk_user_id}",
            "first_name": first_name,
            "last_name": last_name,            
            "phone": phone,
            "email": email,
        },
    )

    changed = []
    if first_name and user.first_name != first_name:
        user.first_name = first_name
        changed.append("first_name")
    if last_name and user.last_name != last_name:
        user.last_name = last_name
        changed.append("last_name")
    if email and user.email != email:
        user.email = email
        changed.append("email")
    if phone and user.phone != phone:
        user.phone = phone
        changed.append("email")
    if avatar and user.avatar_url != avatar:
        user.avatar_url = avatar
        changed.append("avatar_url")

    if changed:
        user.save(update_fields=changed)

    login(request, user)

    request.session.pop("vk_state", None)
    request.session.pop("vk_code_verifier", None)

    return JsonResponse({
        "ok": True,
        "created": created,
        "redirect_url": "/",
    })