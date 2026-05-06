from django.urls import path
from . import views

urlpatterns = [
    path('pdf/<int:commande_id>/', views.generer_facture_pdf, name='generer_pdf'),
]