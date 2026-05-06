from django.db import models
from core.models import Commande

class Facture(models.Model):
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name='facture')
    numero = models.CharField(max_length=50, unique=True)
    date_emission = models.DateTimeField(auto_now_add=True)
    pdf = models.FileField(upload_to='factures/', blank=True, null=True)
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = f"FACT-{self.commande.id:06d}"
        if not self.montant_ttc:
            self.montant_ttc = self.commande.total
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.numero