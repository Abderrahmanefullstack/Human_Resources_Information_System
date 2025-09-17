import re
from django.shortcuts import render, redirect, get_object_or_404
from .models import Entite
from agents.models import Agent  # 👈 IMPORT OBLIGATOIRE
from django import forms
from django.contrib import messages
from django.db.models import Q


class EntiteForm(forms.ModelForm):
    class Meta:
        model = Entite
        fields = ["AffectationCode", "AffectationLibelle", "ArborescenceAffectation"]


def entite_list(request):
    search = request.GET.get("search", "")
    entites = Entite.objects.using("default").all()

    if search:
        # On découpe la recherche en mots et expressions entre guillemets
        parts = re.findall(r'"([^"]+)"|(\S+)', search)
        tokens = [a or b for a, b in parts]

        for tok in tokens:
            entites = entites.filter(
                Q(AffectationCode__icontains=tok)
                | Q(AffectationLibelle__icontains=tok)
                | Q(
                    ArborescenceAffectation__icontains=tok
                )  # <- recherche aussi dans l'arborescence
            )

    entites = entites.order_by("AffectationLibelle")

    return render(
        request,
        "entites/entite_list.html",
        {"entites": entites, "search": search},
    )


def entite_detail(request):
    # id récupéré depuis le bouton "Afficher" de la liste
    code = request.GET.get("selected")
    if not code:
        return redirect("entites:list")  # adapte le name si besoin

    entite = get_object_or_404(
        Entite.objects.using("default"),
        AffectationCode=str(code),
    )

    # Récupérer les agents rattachés à cette entité
    agents_qs = (
        Agent.objects.using("default")
        .filter(AffectationCode=str(entite.AffectationCode))
        .order_by("Nom", "Prenom")
    )

    # Préparer des champs normalisés (certains noms peuvent varier)
    agents = []
    for ag in agents_qs:
        agents.append(
            {
                "Matricule": getattr(ag, "Matricule", ""),
                "Civilite": getattr(ag, "Civilite", ""),
                "Nom": getattr(ag, "Nom", ""),
                "Prenom": getattr(ag, "Prenom", ""),
                "DateNaissance": getattr(ag, "DateNaissance", None),
                # Code / Libellé fonction (on gère plusieurs noms possibles)
                "CodeFonction": (
                    getattr(ag, "FonctionCode", None) or getattr(ag, "CodeFonction", "")
                ),
                "FonctionLibelle": (
                    getattr(ag, "FonctionLibelle", None)
                    or getattr(ag, "LibelleFonction", "")
                ),
                # Date de recrutement (on essaie DateEntree puis un fallback)
                "DateRecrutement": (
                    getattr(ag, "DateEntree", None)
                    or getattr(ag, "DateDebutAdministration", None)
                ),
            }
        )

    return render(
        request,
        "entites/entite_detail.html",
        {
            "entite": entite,
            "agents": agents,  # 👈 utilisé par le template ci-dessous
        },
    )


def entite_update(request):
    code = request.GET.get("selected")
    if not code:
        return redirect("entites:list")
    entite = get_object_or_404(Entite.objects.using("default"), AffectationCode=code)
    if request.method == "POST":
        form = EntiteForm(request.POST, instance=entite)
        if form.is_valid():
            entite = form.save(commit=False)
            entite.save(using="default")
            messages.success(request, "Entité mise à jour avec succès.")
            return redirect("entites:list")
    else:
        form = EntiteForm(instance=entite)
    return render(request, "entites/entite_form.html", {"form": form})


def entite_create(request):
    if request.method == "POST":
        form = EntiteForm(request.POST)
        if form.is_valid():
            entite = form.save(commit=False)
            entite.save(using="default")
            messages.success(request, "Entité créée avec succès.")
            return redirect("entites:list")
    else:
        form = EntiteForm()
    return render(request, "entites/entite_form.html", {"form": form})


def entite_delete(request):
    code = request.GET.get("selected")
    if not code:
        return redirect("entites:list")
    entite = get_object_or_404(Entite.objects.using("default"), AffectationCode=code)
    if request.method == "POST":
        entite.delete(using="default")
        messages.success(request, "Entité supprimée avec succès.")
        return redirect("entites:list")
    return render(request, "entites/entite_confirm_delete.html", {"entite": entite})
