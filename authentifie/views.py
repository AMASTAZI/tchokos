from django.shortcuts import render, redirect
from bd.models import Client, Vendeur, administrator
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login


def signup(request):
    return render(request, 'signup.html')


@csrf_exempt
def signupPost(request):
    if request.method == 'POST':
        nom = request.POST["nom"]
        prenom = request.POST["prenom"]
        username = nom + prenom
        email = request.POST["email"]
        telephone = request.POST["telephone"]
        mdp = request.POST["mdp"]
        confirm_mdp = request.POST["confirm_mdp"]
        # Adresse n'est pas dans le modèle Client, donc on ne la récupère pas ici

        errors = {}
        if not nom:
            errors['nom'] = "Le nom est requis"
        if not prenom:
            errors['prenom'] = "Le prénom est requis"
        if not email:
            errors['email'] = "L'e-mail est requis"
        elif Client.objects.filter(email=email).exists():
            errors['email'] = "Cet email existe déjà."
        if not telephone:
            errors['telephone'] = "Le téléphone est requis"
        if not mdp:
            errors['motdepasse'] = "Le mot de passe est requis"
        elif len(mdp) < 8 or not any(c.isupper() for c in mdp) or not any(c.isdigit() for c in mdp):
            errors['motdepasse'] = "Le mot de passe doit contenir au moins 8 caractères, une majuscule et un chiffre"
        if mdp != confirm_mdp:
            errors['confirmMotdepasse'] = "Les mots de passe ne correspondent pas"

        if errors:
            return JsonResponse({'success': False, 'errors': errors})

        # Création du client
        client = Client.objects.create(
            username=username,
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone,
            mdp=mdp,
            role='C'
        )
        client.set_password(mdp)
        client.save()
        messages.success(request, "Votre compte a bien été créé.")
        return JsonResponse({'success': True, 'message': "Votre compte a bien été créé.", 'redirect': '/authentifie/Connexion/'})

    return redirect('signup')


def login(request):
    return render(request, 'login.html')


@csrf_exempt
def loginPost(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        motdepasse = request.POST.get('motdepasse', '').strip()
        errors = {}

        if not email:
            errors['email'] = "L'e-mail est requis"
        if not motdepasse:
            errors['motdepasse'] = "Le mot de passe est requis"

        if errors:
            return JsonResponse({'success': False, 'errors': errors})

        # Authentification par email pour tous les types d'utilisateurs
        user = None
        # On cherche dans Client, Vendeur, administrator
        try:
            user = Client.objects.get(email=email)
        except Client.DoesNotExist:
            try:
                user = Vendeur.objects.get(email=email)
            except Vendeur.DoesNotExist:
                try:
                    user = administrator.objects.get(email=email)
                except administrator.DoesNotExist:
                    user = None

        if user is not None:
            user_auth = authenticate(request, username=user.username, password=motdepasse)
            if user_auth is not None:
                auth_login(request, user_auth)
                # Redirection selon le rôle
                if hasattr(user_auth, 'role'):
                    if user_auth.role == 'A':
                        redirect_url = '/admin/dashboard/'  # à créer
                    elif user_auth.role == 'V':
                        redirect_url = '/vendeur/dashboard/'  # à créer
                    elif user_auth.role == 'C':
                        redirect_url = '/client/dashboard/'  # à créer
                    else:
                        redirect_url = '/'
                else:
                    redirect_url = '/'
                return JsonResponse({'success': True, 'message': "Connexion réussie !", 'redirect': redirect_url})
        errors['email'] = "Email ou mot de passe incorrect"
        errors['motdepasse'] = "Email ou mot de passe incorrect"
        return JsonResponse({'success': False, 'errors': errors})

    return JsonResponse({'success': False, 'errors': {'global': "Méthode non autorisée"}})


def logout(request):
    from django.contrib.auth import logout as auth_logout
    auth_logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('login')