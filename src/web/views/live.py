# views.py
import requests
from django.conf import settings
from django.views.generic import TemplateView
from django.core.cache import cache
import json

class VKLiveView(TemplateView):
    template_name = "live.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Кэшируем запросы к API (на 5 минут)
        # video_data = cache.get("vk_live_video")
        video_data = None
        if not video_data:
            video_data = self._fetch_vk_video()
            cache.set("vk_live_video", video_data, 300)  # 5 минут
        
        context["player_url"] = video_data.get("player_url")
        context["is_live"] = bool(video_data.get("player_url"))
        return context

    def _fetch_vk_video(self):
        VK_API_URL = "https://api.vk.com/method/video.get"
        params = {
            "owner_id": "-215987094",  # ID пользователя/группы (для групп: -group_id)
            # "filters": "live",  # Только live-видео
            "scope": "video",
            "access_token": settings.VK_ACCESS_TOKEN,
            "v": "5.199"  # Версия API
        }
        
        try:
            response = requests.get(VK_API_URL, params=params)
            print(response)
            data = response.json()
            
            # Обработка ответа
            if "response" in data and data["response"]["items"]:
                video = data["response"]["items"][0]
                return {
                    "player_url": video.get("player"),
                    "title": video.get("title")
                }
        except (requests.RequestException, KeyError, IndexError):
            pass
        
        return {}