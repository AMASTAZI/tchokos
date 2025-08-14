from django.urls import path
from . import views

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    path('produits/', views.produits, name='produits'),
    path('promotions/', views.promotions, name='promotions'),
    path('produit/<int:produit_id>/', views.detail_produit, name='detail_produit'),
    
    # Panier
    path('panier/', views.panier, name='panier'),
    path('ajouter-au-panier/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('modifier-quantite-panier/', views.modifier_quantite_panier, name='modifier_quantite_panier'),
    path('supprimer-du-panier/<int:item_id>/', views.supprimer_du_panier, name='supprimer_du_panier'),
    path('passer-commande/', views.passer_commande, name='passer_commande'),
    
    # Compte utilisateur
    path('mon-compte/', views.mon_compte, name='mon_compte'),
]