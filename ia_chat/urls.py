from django.urls import path
from . import views

urlpatterns = [
    path('api/chat/', views.chat_ollama, name='chat_ollama'),
    path('api/historique/', views.historique_chat, name='historique_chat'),
]