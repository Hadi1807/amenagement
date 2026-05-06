from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('vendeur', 'Vendeur'),
        ('client', 'Client'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

    def is_admin(self):
        return self.role == 'admin'

    def is_vendeur(self):
        return self.role == 'vendeur'