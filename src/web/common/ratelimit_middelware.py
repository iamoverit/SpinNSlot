from django.http import JsonResponse
from django.shortcuts import render
from django_ratelimit.exceptions import RatelimitExceeded

class RatelimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except RatelimitExceeded:
            return render(request, 'error.html', {'message': 'Вы превысили лимит. Попробуйте позже.'})
        return response
