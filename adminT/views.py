# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator

from bd.models import Produit, Commande, CommandeItem, RemiseValidee, Categorie
from adminT.forms import ProduitForm, CategorieForm
import json
from decimal import Decimal

@login_required
def dashboard(request):
    """Vue principale du tableau de bord"""
    if request.user.role != 'A':
        return redirect('/')
    
    # Statistiques
    total_produits = Produit.objects.count()
    total_commandes = Commande.objects.count()
    produits_promotion = RemiseValidee.objects.count()
    revenus = CommandeItem.objects.aggregate(total=Sum('prix'))['total'] or 0
    produits_rupture = Produit.objects.filter(stock=0).count()
    
    context = {
        'total_produits': total_produits,
        'total_commandes': total_commandes,
        'produits_promotion': produits_promotion,
        'revenus': revenus,
        'produits_rupture': produits_rupture,
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def produits_list(request):
    """Liste des produits avec pagination"""
    if request.user.role != 'A':
        return redirect('/')
    
    produits = Produit.objects.select_related('categorie', 'vendeur').all()
    paginator = Paginator(produits, 10)
    page = request.GET.get('page')
    produits_page = paginator.get_page(page)
    
    return render(request, 'admin/produits/list.html', {'produits': produits_page})

@login_required
def ajouter_produit(request):
    """Ajouter un nouveau produit"""
    if request.user.role != 'A':
        return redirect('/')
    
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produit ajouté avec succès!')
            return redirect('admin_panel:produits_list')
    else:
        form = ProduitForm()
    
    return render(request, 'admin/produits/ajouter.html', {'form': form})

@login_required
def modifier_produit(request, pk):
    """Modifier un produit existant"""
    if request.user.role != 'A':
        return redirect('/')
    
    produit = get_object_or_404(Produit, pk=pk)
    
    if request.method == 'POST':
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produit modifié avec succès!')
            return redirect('admin_panel:produits_list')
    else:
        form = ProduitForm(instance=produit)
    
    return render(request, 'admin/produits/modifier.html', {'form': form, 'produit': produit})

@login_required
def supprimer_produit(request, pk):
    """Supprimer un produit"""
    if request.user.role != 'A':
        return redirect('/')
    
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        produit.delete()
        messages.success(request, 'Produit supprimé avec succès!')
        return redirect('admin_panel:produits_list')
    
    return render(request, 'admin/produits/supprimer.html', {'produit': produit})

@login_required
@require_http_methods(["POST"])
def casser_prix(request, pk):
    """Appliquer une réduction sur un produit"""
    if request.user.role != 'A':
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    produit = get_object_or_404(Produit, pk=pk)
    data = json.loads(request.body)
    
    if 'pourcentage' in data:
        pourcentage = int(data['pourcentage'])
        nouveau_prix = produit.prix * (100 - pourcentage) / 100
    elif 'nouveau_prix' in data:
        nouveau_prix = Decimal(data['nouveau_prix'])
        pourcentage = int((1 - nouveau_prix / produit.prix) * 100)
    else:
        return JsonResponse({'error': 'Données invalides'}, status=400)
    
    # Créer une remise validée
    RemiseValidee.objects.create(
        produit=produit,
        pourcentage=pourcentage
    )
    
    # Mettre à jour le prix du produit
    produit.prix = nouveau_prix
    produit.save()
    
    return JsonResponse({
        'success': True,
        'nouveau_prix': float(nouveau_prix),
        'pourcentage': pourcentage
    })

@login_required
def promotions_list(request):
    """Liste des promotions actives"""
    if request.user.role != 'A':
        return redirect('/')
    
    promotions = RemiseValidee.objects.select_related('produit').all()
    return render(request, 'admin/promotions/list.html', {'promotions': promotions})

@login_required
def commandes_list(request):
    """Liste des commandes"""
    if request.user.role != 'A':
        return redirect('/')
    
    commandes = Commande.objects.select_related('client').prefetch_related('commandeitem_set__produit').all()
    paginator = Paginator(commandes, 15)
    page = request.GET.get('page')
    commandes_page = paginator.get_page(page)
    
    return render(request, 'admin/commandes/list.html', {'commandes': commandes_page})

@login_required
@require_http_methods(["POST"])
def changer_statut_commande(request, pk):
    """Changer le statut d'une commande"""
    if request.user.role != 'A':
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    commande = get_object_or_404(Commande, pk=pk)
    nouveau_statut = request.POST.get('statut')
    
    if nouveau_statut in ['en_attente', 'en_cours', 'livre', 'annule']:
        commande.statut = nouveau_statut
        commande.save()
        return JsonResponse({'success': True, 'statut': nouveau_statut})
    
    return JsonResponse({'error': 'Statut invalide'}, status=400)

@login_required
def utilisateurs_list(request):
    """Liste des utilisateurs"""
    if request.user.role != 'A':
        return redirect('/')
    
    clients = Client.objects.annotate(nb_commandes=Count('commande')).all()
    paginator = Paginator(clients, 20)
    page = request.GET.get('page')
    clients_page = paginator.get_page(page)
    
    return render(request, 'admin/utilisateurs/list.html', {'clients': clients_page})

@login_required
def parametres(request):
    """Page des paramètres"""
    if request.user.role != 'A':
        return redirect('/')
    
    return render(request, 'admin/parametres/index.html')

@login_required
def categories_list(request):
    """Gestion des catégories"""
    if request.user.role != 'A':
        return redirect('/')
    
    categories = Categorie.objects.all()
    return render(request, 'admin/parametres/categories.html', {'categories': categories})

@login_required
def annuler_promotion(request, pk):
    """Annuler une promotion"""
    if request.user.role != 'A':
        return redirect('/')
    
    promotion = get_object_or_404(RemiseValidee, pk=pk)
    if request.method == 'POST':
        promotion.delete()
        messages.success(request, 'Promotion annulée avec succès!')
        return redirect('admin_panel:promotions_list')
    
    return render(request, 'admin/promotions/annuler.html', {'promotion': promotion})

@login_required
def bloquer_utilisateur(request, pk):
    """Bloquer/débloquer un utilisateur"""
    if request.user.role != 'A':
        return redirect('/')
    
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.is_active = not client.is_active
        client.save()
        statut = "bloqué" if not client.is_active else "débloqué"
        messages.success(request, f'Utilisateur {statut} avec succès!')
        return redirect('admin_panel:utilisateurs_list')
    
    return render(request, 'admin/utilisateurs/bloquer.html', {'client': client})

@login_required
def ajouter_categorie(request):
    """Ajouter une catégorie"""
    if request.user.role != 'A':
        return redirect('/')
    
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Catégorie ajoutée avec succès!')
            return redirect('admin_panel:categories_list')
    else:
        form = CategorieForm()
    
    return render(request, 'admin/parametres/ajouter_categorie.html', {'form': form})