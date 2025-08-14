# urls.py
from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Gestion des produits
    path('produits/', views.produits_list, name='produits_list'),
    path('produits/ajouter/', views.ajouter_produit, name='ajouter_produit'),
    path('produits/modifier/<int:pk>/', views.modifier_produit, name='modifier_produit'),
    path('produits/supprimer/<int:pk>/', views.supprimer_produit, name='supprimer_produit'),
    path('produits/casser-prix/<int:pk>/', views.casser_prix, name='casser_prix'),
    
    # Promotions
    path('promotions/', views.promotions_list, name='promotions_list'),
    path('promotions/annuler/<int:pk>/', views.annuler_promotion, name='annuler_promotion'),
    
    # Commandes
    path('commandes/', views.commandes_list, name='commandes_list'),
    path('commandes/statut/<int:pk>/', views.changer_statut_commande, name='changer_statut_commande'),
    
    # Utilisateurs
    path('utilisateurs/', views.utilisateurs_list, name='utilisateurs_list'),
    path('utilisateurs/bloquer/<int:pk>/', views.bloquer_utilisateur, name='bloquer_utilisateur'),
    
    # Paramètres
    path('parametres/', views.parametres, name='parametres'),
    path('categories/', views.categories_list, name='categories_list'),
    path('categories/ajouter/', views.ajouter_categorie, name='ajouter_categorie'),
]