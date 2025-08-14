from django.urls import path
from .import views


urlpatterns = [
    path('Inscription/', views.signup, name='signup'),
    path('InscriptionPost/', views.signupPost, name='signup_post'),
    path('Connexion/', views.login, name='login'),
    path('ConnexionPost/', views.loginPost, name='login_post'),
    path('Deconnexion/', views.logout, name='logout'),
]
