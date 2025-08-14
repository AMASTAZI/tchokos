# forms.py
from django import forms
from bd.models import Produit, Categorie, Vendeur

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'description', 'prix', 'stock', 'categorie', 'vendeur', 'statut']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du produit'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description du produit'
            }),
            'prix': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'categorie': forms.Select(attrs={
                'class': 'form-select'
            }),
            'vendeur': forms.Select(attrs={
                'class': 'form-select'
            }),
            'statut': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('disponible', 'Disponible'),
                ('indisponible', 'Indisponible'),
                ('rupture', 'Rupture de stock')
            ])
        }

class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la catégorie'
            })
        }