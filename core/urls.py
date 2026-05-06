from django.urls import path
from . import views

urlpatterns = [
    path('clients/', views.clients_page, name='clients'),
    path('meubles/', views.meubles_page, name='meubles'),
    path('commandes/', views.commandes_page, name='commandes'),
    path('api/clients/', views.api_clients, name='api_clients'),
    path('api/meubles/', views.api_meubles, name='api_meubles'),
    path('api/commandes/', views.api_commandes, name='api_commandes'),
    path('api/commandes/<int:commande_id>/', views.api_commande_detail, name='api_commande_detail'),
]