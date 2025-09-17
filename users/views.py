from django.db import connections
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from vivier.models import (
    Vivier,
)
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect
from django.urls import reverse
from agents.models import Agent, ImportLog
from fonctions.models import Fonction
from annonces.models import AnnonceRH
from entites.models import Entite
from django.shortcuts import render
from agents.models import ImportLog
from django.utils import timezone
import time
from django.utils import timezone
from django.db.models import Q


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Connexion :
    - messages toasts (succès/erreur)
    - petit délai anti brute force
    - redirection propre
    """
    # Nettoyage ciblé d’un ancien message parasite (si tu y tiens)
    storage = messages.get_messages(request)
    for m in storage:
        if "connections" in str(m).lower():
            storage.used = True

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            messages.error(
                request, "Tous les champs sont obligatoires", extra_tags="danger"
            )
            return render(request, "users/login.html")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # (optionnel) stocker l’instant de connexion si tu veux l’afficher ailleurs
            request.session["logged_in_at"] = timezone.now().isoformat()

            # ✅ message toast de succès
            messages.success(
                request, f"Bienvenue {user.username} 👋 Connexion réussie !"
            )

            next_url = (
                request.GET.get("next") or request.POST.get("next") or "agents:list"
            )
            return redirect(next_url)
        else:
            messages.error(request, "Identifiants incorrects", extra_tags="danger")
            time.sleep(2)  # anti brute force

    return render(request, "users/login.html")


@require_http_methods(["POST"])
def logout_view(request):
    """
    Vue de déconnexion sécurisée :
    - Uniquement en POST
    - Message de confirmation
    - Suppression de la session
    """
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès")
    response = HttpResponseRedirect(reverse("users:login"))
    # Nettoyage des cookies de session
    response.delete_cookie("sessionid")
    return response


# @login_required
# def home(request):
# """
# Vue d'accueil protégée :
# - Redirige automatiquement si non authentifié
# - Contexte personnalisable
# """
# context = {"welcome_message": f"Bienvenue, {request.user.username}"}
# return render(request, "home.html", context)


class CustomLoginView(LoginView):
    """
    Variante de login_view en classe :
    - Hérite des fonctionnalités standards
    - Surcharge pour le nettoyage des messages
    - Utilisable comme alternative
    """

    def get(self, request, *args, **kwargs):
        # Nettoyage des messages existants
        list(messages.get_messages(request))  # Vide la storage
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Ajout d'un délai anti-brute force
        import time

        time.sleep(1)
        return super().post(request, *args, **kwargs)


def home(request):
    nb_agents = Agent.objects.count()
    nb_fonctions = Fonction.objects.count()
    nb_entites = Entite.objects.count()
    nb_hommes = Agent.objects.filter(Civilite__iexact="Mr").count()
    nb_femmes = Agent.objects.filter(Civilite__in=["Mme", "Melle"]).count()
    recent_imports = ImportLog.objects.order_by("-import_date")[:1]

    today = timezone.localdate()  # date (pas datetime)

    # 1) Filtre “annonces actives aujourd’hui”
    qs = (
        AnnonceRH.objects.filter(actif=True)
        .filter(Q(date_debut__isnull=True) | Q(date_debut__lte=today))
        .filter(Q(date_fin__isnull=True) | Q(date_fin__gte=today))
        .order_by("-created_at")
    )
    annonces = list(qs[:3])
    if not annonces:
        annonces = list(
            AnnonceRH.objects.filter(actif=True).order_by("-created_at")[:3]
        )

    # <-- AJOUT : viviers non actifs (max 4)
    viviers_inactifs = Vivier.objects.filter(Valide=False).order_by("-DateCreation")[:4]

    return render(
        request,
        "home.html",
        {
            "nb_agents": nb_agents,
            "nb_fonctions": nb_fonctions,
            "nb_entites": nb_entites,
            "nb_hommes": nb_hommes,
            "nb_femmes": nb_femmes,
            "recent_imports": recent_imports,
            "annonces": annonces,  # conservé
            "viviers_inactifs": viviers_inactifs,  # <-- AJOUT
        },
    )
