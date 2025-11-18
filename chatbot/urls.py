from django.urls import path
from . import views

urlpatterns = [
    path('get_response/', views.get_response, name='get_response'),
]