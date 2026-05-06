from django.db import models
from django.contrib.auth.models import User

class Client(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    adresse = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nom

class Meuble(models.Model):
    CATEGORIES = [
        ('salon', 'Salon'),
        ('chambre', 'Chambre'),
        ('cuisine', 'Cuisine'),
        ('bureau', 'Bureau'),
        ('salle_de_bain', 'Salle de bain'),
        ('exterieur', 'Extérieur'),
    ]
    nom = models.CharField(max_length=200)
    description = models.TextField()
    categorie = models.CharField(max_length=50, choices=CATEGORIES)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='meubles/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.nom} ({self.prix}€)"

class Commande(models.Model):
    STATUTS = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('livree', 'Livrée'),
        ('payee', 'Payée'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    vendeur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"CMD-{self.id:04d} - {self.client.nom}"
    
    def calculer_total(self):
        total = sum(ligne.sous_total() for ligne in self.lignes.all())
        self.total = total
        self.save()
        return total

class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, related_name='lignes', on_delete=models.CASCADE)
    meuble = models.ForeignKey(Meuble, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)  # Historique prix
    
    def sous_total(self):
        return self.quantite * self.prix_unitaire