from django.shortcuts import render



# Create your views here.
from django.http import JsonResponse
from .ai import get_chatbot_response


def get_response(request):
    user_message = request.GET.get('msg')
    bot_reply = get_chatbot_response(user_message)
    return JsonResponse({'reply': bot_reply})