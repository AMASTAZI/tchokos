from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator

from bd.models import Categorie, Commande, CommandeItem, Panier, PanierItem, Produit, RemiseValidee
from .models import *
import json

def home(request):
    """Page d'accueil avec carrousel et produits en vedette"""
    categories = Categorie.objects.all()
    
    # Nouveautés (5 derniers produits)
    nouveautes = Produit.objects.filter(statut='disponible').order_by('-id')[:8]
    
    # Meilleures ventes (simulation avec les produits ayant le moins de stock)
    meilleures_ventes = Produit.objects.filter(statut='disponible').order_by('stock')[:8]
    
    # Produits en promotion
    produits_promo = []
    remises = RemiseValidee.objects.select_related('produit')[:6]
    for remise in remises:
        produit = remise.produit
        prix_reduit = float(produit.prix) * (1 - remise.pourcentage / 100)
        produits_promo.append({
            'produit': produit,
            'prix_original': produit.prix,
            'prix_reduit': prix_reduit,
            'pourcentage': remise.pourcentage
        })
    
    context = {
        'categories': categories,
        'nouveautes': nouveautes,
        'meilleures_ventes': meilleures_ventes,
        'produits_promo': produits_promo,
    }
    return render(request, 'store/home.html', context)

def produits(request):
    """Page des produits avec filtres"""
    produits_list = Produit.objects.filter(statut='disponible').select_related('categorie', 'vendeur')
    categories = Categorie.objects.all()
    
    # Filtres
    categorie_id = request.GET.get('categorie')
    prix_min = request.GET.get('prix_min')
    prix_max = request.GET.get('prix_max')
    search = request.GET.get('search')
    
    if categorie_id:
        produits_list = produits_list.filter(categorie_id=categorie_id)
    
    if prix_min:
        produits_list = produits_list.filter(prix__gte=prix_min)
    
    if prix_max:
        produits_list = produits_list.filter(prix__lte=prix_max)
    
    if search:
        produits_list = produits_list.filter(
            Q(nom__icontains=search) | Q(description__icontains=search)
        )
    
    # Récupérer les remises validées
    remises = {}
    for remise in RemiseValidee.objects.select_related('produit'):
        prix_reduit = float(remise.produit.prix) * (1 - remise.pourcentage / 100)
        remises[remise.produit.id] = {
            'pourcentage': remise.pourcentage,
            'prix_reduit': prix_reduit
        }
    
    # Pagination
    paginator = Paginator(produits_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'remises': remises,
        'current_filters': {
            'categorie': categorie_id,
            'prix_min': prix_min,
            'prix_max': prix_max,
            'search': search,
        }
    }
    return render(request, 'store/produits.html', context)

def promotions(request):
    """Page des promotions - Les prix ont été cassés"""
    remises = RemiseValidee.objects.select_related('produit').filter(produit__statut='disponible')
    
    produits_promo = []
    for remise in remises:
        produit = remise.produit
        prix_reduit = float(produit.prix) * (1 - remise.pourcentage / 100)
        produits_promo.append({
            'produit': produit,
            'prix_original': produit.prix,
            'prix_reduit': prix_reduit,
            'pourcentage': remise.pourcentage
        })
    
    # Pagination
    paginator = Paginator(produits_promo, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'store/promotions.html', context)

@login_required
def panier(request):
    """Page du panier"""
    try:
        panier = Panier.objects.get(client=request.user.client)
        items = PanierItem.objects.filter(panier=panier).select_related('produit')
    except (Panier.DoesNotExist, AttributeError):
        items = []
    
    # Calculer les totaux avec les remises
    total = 0
    items_with_prices = []
    
    for item in items:
        # Vérifier s'il y a une remise
        try:
            remise = RemiseValidee.objects.get(produit=item.produit)
            prix_unitaire = float(item.produit.prix) * (1 - remise.pourcentage / 100)
        except RemiseValidee.DoesNotExist:
            prix_unitaire = float(item.produit.prix)
        
        prix_total_item = prix_unitaire * item.quantite
        total += prix_total_item
        
        items_with_prices.append({
            'item': item,
            'prix_unitaire': prix_unitaire,
            'prix_total': prix_total_item
        })
    
    context = {
        'items_with_prices': items_with_prices,
        'total': total,
    }
    return render(request, 'store/panier.html', context)

@login_required
def ajouter_au_panier(request, produit_id):
    """Ajouter un produit au panier"""
    if request.method == 'POST':
        produit = get_object_or_404(Produit, id=produit_id)
        quantite = int(request.POST.get('quantite', 1))
        
        try:
            client = request.user.client
            panier, created = Panier.objects.get_or_create(client=client)
            
            item, created = PanierItem.objects.get_or_create(
                panier=panier,
                produit=produit,
                defaults={'quantite': quantite}
            )
            
            if not created:
                item.quantite += quantite
                item.save()
            
            messages.success(request, f'{produit.nom} ajouté au panier!')
            
        except AttributeError:
            messages.error(request, 'Erreur: Vous devez être connecté comme client.')
    
    return redirect('produits')

@login_required
def modifier_quantite_panier(request):
    """Modifier la quantité d'un produit dans le panier"""
    if request.method == 'POST':
        data = json.loads(request.body)
        item_id = data.get('item_id')
        nouvelle_quantite = data.get('quantite')
        
        try:
            item = PanierItem.objects.get(id=item_id, panier__client=request.user.client)
            if nouvelle_quantite <= 0:
                item.delete()
            else:
                item.quantite = nouvelle_quantite
                item.save()
            
            return JsonResponse({'success': True})
        except PanierItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Produit non trouvé'})
    
    return JsonResponse({'success': False})

@login_required
def supprimer_du_panier(request, item_id):
    """Supprimer un produit du panier"""
    try:
        item = PanierItem.objects.get(id=item_id, panier__client=request.user.client)
        item.delete()
        messages.success(request, 'Produit supprimé du panier!')
    except PanierItem.DoesNotExist:
        messages.error(request, 'Produit non trouvé dans le panier.')
    
    return redirect('panier')

@login_required
def passer_commande(request):
    """Passer une commande"""
    try:
        client = request.user.client
        panier = Panier.objects.get(client=client)
        items = PanierItem.objects.filter(panier=panier)
        
        if not items.exists():
            messages.error(request, 'Votre panier est vide!')
            return redirect('panier')
        
        # Créer la commande
        commande = Commande.objects.create(client=client)
        
        # Créer les items de commande
        for item in items:
            # Calculer le prix avec remise si applicable
            try:
                remise = RemiseValidee.objects.get(produit=item.produit)
                prix = float(item.produit.prix) * (1 - remise.pourcentage / 100)
            except RemiseValidee.DoesNotExist:
                prix = item.produit.prix
            
            CommandeItem.objects.create(
                commande=commande,
                produit=item.produit,
                quantite=item.quantite,
                prix=prix
            )
            
            # Réduire le stock
            item.produit.stock -= item.quantite
            item.produit.save()
        
        # Vider le panier
        items.delete()
        
        messages.success(request, f'Commande #{commande.id} passée avec succès!')
        return redirect('mon_compte')
        
    except (Panier.DoesNotExist, AttributeError):
        messages.error(request, 'Erreur lors de la commande.')
        return redirect('panier')

@login_required
def mon_compte(request):
    """Page du compte utilisateur"""
    try:
        client = request.user.client
        commandes = Commande.objects.filter(client=client).order_by('-date')[:10]
        
        context = {
            'client': client,
            'commandes': commandes,
        }
        return render(request, 'store/mon_compte.html', context)
    except AttributeError:
        messages.error(request, 'Accès refusé.')
        return redirect('home')

def detail_produit(request, produit_id):
    """Page de détail d'un produit"""
    produit = get_object_or_404(Produit, id=produit_id)
    
    # Vérifier s'il y a une remise
    remise_info = None
    try:
        remise = RemiseValidee.objects.get(produit=produit)
        prix_reduit = float(produit.prix) * (1 - remise.pourcentage / 100)
        remise_info = {
            'pourcentage': remise.pourcentage,
            'prix_reduit': prix_reduit
        }
    except RemiseValidee.DoesNotExist:
        pass
    
    # Produits similaires (même catégorie)
    produits_similaires = Produit.objects.filter(
        categorie=produit.categorie,
        statut='disponible'
    ).exclude(id=produit.id)[:4]
    
    context = {
        'produit': produit,
        'remise_info': remise_info,
        'produits_similaires': produits_similaires,
    }
    return render(request, 'store/detail_produit.html', context)