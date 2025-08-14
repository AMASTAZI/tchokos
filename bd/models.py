from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser

#Utilisateur personnalisé
class User(AbstractUser):
    ROLES = (
        ('A', 'Administrateur'),
        ('V', 'Vendeur'),
        ('C', 'Client'),
    )
    role = models.CharField(max_length=10, choices=ROLES)

    username = models.CharField(max_length=150, unique=True)
    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    mdp = models.CharField(max_length=100)
    class Meta:
        swappable = 'AUTH_USER_MODEL'

class Client(User):
    
    idClient = models.AutoField(primary_key=True)

    def str(self):
        return f"Passer commande pour {self.nom} {self.prenom}"
    def str(self):
        return f"Voir commande pour {self.nom} {self.prenom}"
    
   
    


class Vendeur(User):
    idVendeur = models.AutoField(primary_key=True)
   
    

class administrator(User):
    id_admin = models.AutoField(primary_key=True)
    
   
class Categorie(models.Model):
    nom = models.CharField(max_length=100)

    def str(self):
        return self.nom

class Produit(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    vendeur = models.ForeignKey(Vendeur, on_delete=models.CASCADE)
    statut = models.CharField(max_length=100, default="disponible")

class RemiseProposee(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    vendeur = models.ForeignKey(Vendeur, on_delete=models.CASCADE)
    pourcentage_propose = models.PositiveIntegerField()
    statut = models.CharField(max_length=20, choices=[('en_attente', 'En attente'), ('valide', 'Validée'), ('rejete', 'Rejetée')], default='en_attente')
    date_proposition = models.DateTimeField(auto_now_add=True)

class RemiseValidee(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    pourcentage = models.PositiveIntegerField()
    date_validation = models.DateTimeField(auto_now_add=True)

class Panier(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE)

class PanierItem(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()

class Commande(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50, default="en_attente")

class CommandeItem(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)

class Livraison(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    vendeur = models.ForeignKey(Vendeur, on_delete=models.CASCADE)
    statut = models.CharField(max_length=50, default="en_attente")
    date_livraison = models.DateTimeField(null=True, blank=True)
class Avis(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    vendeur = models.ForeignKey(Vendeur, on_delete=models.CASCADE)
    note = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # Note de 1 à 5
    commentaire = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('client', 'vendeur')  # Un seul avis par client/vendeur

   
