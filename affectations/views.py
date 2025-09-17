import re
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import date
import tempfile
import os
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
)  # <- ajoute BadRequest
from django.conf import settings
from django.contrib.staticfiles import finders  # <- pour résoudre /static/
from docxtpl import DocxTemplate

from reportlab.pdfgen import canvas  # (tu peux laisser si tu t’en sers ailleurs)
from reportlab.lib.pagesizes import A4
from django import forms
from django.contrib.auth.decorators import login_required
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa

from entites.models import Entite
from fonctions.models import Fonction
from .models import Affectation
from .forms import (
    ChoixAgentForm,
    ChoixTypeForm,
    AffectationStep1Form,
    AffectationStep2Form,
)
from agents.models import Agent


@login_required
# affectations/views.py


def affectation_list(request):
    q = (request.GET.get("q") or "").strip()

    # 1) Charger les affectations depuis la bonne base
    qs = Affectation.objects.using("default").all()

    # 2) Filtre simple (N° affectation ou matricule)
    if q:
        qs = qs.filter(Q(NumeroAffectation__icontains=q) | Q(Matricule__icontains=q))

    # 3) Ordre le plus pertinent (dates récentes en premier)
    qs = qs.order_by("-DateLettreAffectation", "-DateMobilite", "-NumeroAffectation")

    # 4) Récupérer les agents correspondants en un seul coup
    matricules = [str(a.Matricule) for a in qs]
    agent_map = {
        str(ag.Matricule): ag
        for ag in Agent.objects.using("default").filter(Matricule__in=matricules)
    }

    # 5) Construire des lignes prêtes pour le template
    rows = []
    for a in qs:
        ag = agent_map.get(str(a.Matricule))

        # “Récents” = le nouveau si présent, sinon l’ancien (fallback)
        f_code_recent = (
            a.CodeFonctionNouveau
            or a.CodeFonctionAncien
            or (getattr(ag, "FonctionCode", "") if ag else "")
        )
        f_lib_recent = (
            a.LibelleFonctionNouveau
            or a.LibelleFonctionAncien
            or (getattr(ag, "FonctionLibelle", "") if ag else "")
        )
        e_code_recent = (
            a.CodeEntiteNouveau
            or a.CodeEntiteAncien
            or (getattr(ag, "AffectationCode", "") if ag else "")
        )
        e_lib_recent = (
            a.LibelleEntiteNouveau
            or a.LibelleEntiteAncien
            or (getattr(ag, "AffectationLibelle", "") if ag else "")
        )

        rows.append(
            {
                "NumeroAffectation": a.NumeroAffectation,
                "DateLettreAffectation": a.DateLettreAffectation,
                "Matricule": a.Matricule,
                "Civilite": getattr(ag, "Civilite", "") if ag else "",
                "Nom": getattr(ag, "Nom", "") if ag else "",
                "Prenom": getattr(ag, "Prenom", "") if ag else "",
                "DateNaissance": getattr(ag, "DateNaissance", None) if ag else None,
                "ChangementAffectation": a.ChangementAffectation,
                "ChangementFonction": a.ChangementFonction,
                "FonctionRecenteCode": f_code_recent,
                "FonctionRecenteLibelle": f_lib_recent,
                "AffectationRecenteCode": e_code_recent,
                "AffectationRecenteLibelle": e_lib_recent,
                "LieuFonction": (
                    getattr(ag, "ArborescenceAffectation", "") if ag else ""
                ),
            }
        )

    # 6) Rendu (le template peut boucler sur 'affectations' comme avant)
    return render(
        request,
        "affectations/affectation_list.html",
        {
            "affectations": rows,
            "q": q,
        },
    )


def affectation_detail(request, pk):
    a = get_object_or_404(Affectation, pk=pk)
    agent = Agent.objects.using("default").filter(Matricule=a.Matricule).first()
    return render(
        request, "affectations/affectation_detail.html", {"a": a, "agent": agent}
    )


DOCX_TYPES = {
    "aff1": {
        "label": "Lettre d’affectation — Modèle 1",
        "docx": "Aff1.docx",
        "filename": lambda c: f"Lettre_Affectation_{c['num']}_Aff1.docx",
    },
    "aff2": {
        "label": "Lettre d’affectation — Modèle 2",
        "docx": "Aff2.docx",
        "filename": lambda c: f"Lettre_Affectation_{c['num']}_Aff2.docx",
    },
    "aff3": {
        "label": "Lettre d’affectation — Modèle 3",
        "docx": "Aff3.docx",
        "filename": lambda c: f"Lettre_Affectation_{c['num']}_Aff3.docx",
    },
}


def _affectation_context(a, agent=None):
    return {
        "num": getattr(a, "NumeroAffectation", "") or "",
        "date_lettre": getattr(a, "DateLettreAffectation", None),
        "matricule": getattr(a, "Matricule", "") or "",
        "civilite": getattr(agent, "Civilite", "") if agent else "",
        "nom": getattr(agent, "Nom", "") if agent else "",
        "prenom": getattr(agent, "Prenom", "") if agent else "",
        "date_nais": getattr(agent, "DateNaissance", None) if agent else None,
        "anc_aff_code": getattr(a, "CodeEntiteAncien", "") or "",
        "anc_aff_lib": getattr(a, "LibelleEntiteAncien", "") or "",
        "anc_date_aff": getattr(a, "DateAffectationAncien", None),
        "anc_fct_code": getattr(a, "CodeFonctionAncien", "") or "",
        "anc_fct_lib": getattr(a, "LibelleFonctionAncien", "") or "",
        "anc_date_fct": getattr(a, "DateFonctionAncien", None),
        "nv_aff_code": getattr(a, "CodeEntiteNouveau", "") or "",
        "nv_aff_lib": getattr(a, "LibelleEntiteNouveau", "") or "",
        "nv_date_aff": getattr(a, "DateAffectationNouveau", None),
        "nv_fct_code": getattr(a, "CodeFonctionNouveau", "") or "",
        "nv_fct_lib": getattr(a, "LibelleFonctionNouveau", "") or "",
        "nv_date_fct": getattr(a, "DateFonctionNouveau", None),
        "arbo": getattr(agent, "ArborescenceAffectation", "") if agent else "",
    }


def _get_docx_template_path(filename: str) -> str:
    """
    Retourne un chemin absolu vers le .docx modèle.
    1) via staticfiles (affectations/<filename>)
    2) via settings.DOCX_TEMPLATES_DIR si défini
    3) via <BASE_DIR>/static/affectations/<filename>
    """
    # 1) Staticfiles (recommandé en dev et prod)
    found = finders.find(f"affectations/{filename}")
    if found and os.path.exists(found):
        return found

    # 2) Dossier custom optionnel
    base_dir = getattr(settings, "DOCX_TEMPLATES_DIR", None)
    if base_dir:
        p = os.path.join(str(base_dir), filename)
        if os.path.exists(p):
            return p

    # 3) Fallback sur static du projet
    p = os.path.join(settings.BASE_DIR, "static", "affectations", filename)
    if os.path.exists(p):
        return p

    raise Http404(f"Modèle introuvable : affectations/{filename} (static/affectations)")


def _safe_filename(name: str) -> str:
    # Remplace tous les caractères invalides Windows par des tirets
    return re.sub(r'[\\/:*?"<>|]+', "-", name)


def _date_fr(d):
    """Retourne 'dd/mm/YYYY' ou '' si None/vidé."""
    try:
        if not d:
            return ""
        if isinstance(d, (date,)):
            return d.strftime("%d/%m/%Y")
        # fallback: strings/DateTime
        return str(d)
    except Exception:
        return ""


def _civilites(agent):
    raw = (getattr(agent, "Civilite", "") or "").strip().lower()
    # Adapte si tes valeurs sont 'M', 'Mr', 'Madame', etc.
    if raw in {"m", "mr", "monsieur"}:
        return ("M.", "Monsieur")
    if raw in {"mme", "madame"}:
        return ("Mme", "Madame")
    # défaut neutre
    return ("M.", "Monsieur")


def _affectation_context(a, agent=None):
    civ_short, civ_long = _civilites(agent)
    ctx = {
        "num": getattr(a, "NumeroAffectation", "") or "",
        "date_lettre": getattr(a, "DateLettreAffectation", None),
        "matricule": getattr(a, "Matricule", "") or "",
        "civilite": getattr(agent, "Civilite", "") if agent else "",
        "civ_short": civ_short,
        "civ_long": civ_long,
        "nom": getattr(agent, "Nom", "") if agent else "",
        "prenom": getattr(agent, "Prenom", "") if agent else "",
        "date_nais": getattr(agent, "DateNaissance", None) if agent else None,
        # ANCIEN
        "anc_aff_code": getattr(a, "CodeEntiteAncien", "") or "",
        "anc_aff_lib": getattr(a, "LibelleEntiteAncien", "") or "",
        "anc_date_aff": getattr(a, "DateAffectationAncien", None),
        "anc_fct_code": getattr(a, "CodeFonctionAncien", "") or "",
        "anc_fct_lib": getattr(a, "LibelleFonctionAncien", "") or "",
        "anc_date_fct": getattr(a, "DateFonctionAncien", None),
        # NOUVEAU
        "nv_aff_code": getattr(a, "CodeEntiteNouveau", "") or "",
        "nv_aff_lib": getattr(a, "LibelleEntiteNouveau", "") or "",
        "nv_date_aff": getattr(a, "DateAffectationNouveau", None),
        "nv_fct_code": getattr(a, "CodeFonctionNouveau", "") or "",
        "nv_fct_lib": getattr(a, "LibelleFonctionNouveau", "") or "",
        "nv_date_fct": getattr(a, "DateFonctionNouveau", None),
        "arbo": getattr(agent, "ArborescenceAffectation", "") if agent else "",
    }
    return ctx


def affectation_docx(request, pk):
    # Récup données
    a = get_object_or_404(Affectation, pk=pk)
    agent = Agent.objects.using("default").filter(Matricule=a.Matricule).first()

    # Type (aff1/aff2/aff3)
    docx_type = (request.GET.get("type") or "").lower()
    cfg = DOCX_TYPES.get(docx_type)
    if not cfg:
        return HttpResponseBadRequest(
            "Paramètre 'type' manquant ou invalide (aff1, aff2, aff3)."
        )

    # Contexte pour docx
    ctx = _affectation_context(a, agent)
    ctx.update(
        {
            "ville": "Tanger",
            "reseau": ctx.get("arbo"),
            "sign_gauche_nom": "DOHRI CHAKER",
            "sign_gauche_role": "DIRECTEUR PRINCIPAL",
            "sign_droite_nom": "AFFANE MOHAMED",
            "sign_droite_role": "PRÉSIDENT DU DIRECTOIRE",
            "directeur_reseau": "",
        }
    )

    # Localise le modèle .docx
    template_docx = _get_docx_template_path(cfg["docx"])

    # Rendu docx -> téléchargement direct
    with tempfile.TemporaryDirectory() as tmpdir:
        raw_name = cfg["filename"](ctx)  # ex: "Lettre_Affectation_003/2025_Aff1.docx"
        safe_name = _safe_filename(
            raw_name
        )  # ex: "Lettre_Affectation_003-2025_Aff1.docx"
        out_docx = os.path.join(tmpdir, safe_name)

        doc = DocxTemplate(template_docx)
        doc.jinja_env.filters["date_fr"] = _date_fr
        doc.render(ctx)
        doc.save(out_docx)

        with open(out_docx, "rb") as f:
            resp = HttpResponse(
                f.read(),
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            resp["Content-Disposition"] = f'attachment; filename="{safe_name}"'
            return resp


def affectation_start(request):
    # reset du wizard
    for k in ("aff_mat", "aff_mat_list", "aff_mat_index", "aff_type", "aff_candidates"):
        request.session.pop(k, None)
    return redirect("affectations:choose_type")  # 👈 on commence par le type


def affectation_choose_agent(request):
    type_aff = request.session.get("aff_type")
    if not type_aff:
        return redirect("affectations:choose_type")

    form = ChoixAgentForm(request.GET or None)
    agents = Agent.objects.using("default").all()

    if form.is_valid():
        q = form.cleaned_data.get("q", "").strip()
        if q:
            agents = agents.filter(
                Q(Matricule__icontains=q) | Q(Nom__icontains=q) | Q(Prenom__icontains=q)
            )

    # Règles selon le type
    rules = {
        "FONCTION": {"min": 1, "max": None, "hint": "Sélection libre (1 ou plusieurs)"},
        "AGENCE": {"min": 1, "max": 3, "hint": "Maximum 3 agents"},
        "LES_DEUX": {"min": 1, "max": 1, "hint": "Un seul agent"},
    }
    rule = rules[type_aff]

    if request.method == "POST":
        selected_list = request.POST.getlist("selected")
        n = len(selected_list)

        if n < rule["min"]:
            messages.error(request, f"Sélectionnez au moins {rule['min']} agent(s).")
        elif rule["max"] is not None and n > rule["max"]:
            messages.error(
                request, f"Vous pouvez sélectionner au maximum {rule['max']} agent(s)."
            )
        else:
            # OK → pose la sélection pour le wizard
            for k in ("aff_mat", "aff_mat_list", "aff_mat_index"):
                request.session.pop(k, None)

            if n == 1:
                request.session["aff_mat"] = selected_list[0]
            else:
                request.session["aff_mat_list"] = selected_list
                request.session["aff_mat_index"] = 0

            return redirect("affectations:step1")

    return render(
        request,
        "affectations/choose_agent.html",
        {"form": form, "agents": agents, "type_aff": type_aff, "rule": rule},
    )


def affectation_delete(request):
    pk = request.GET.get("selected")
    if not pk:
        return redirect("affectations:list")
    a = get_object_or_404(Affectation, pk=pk)
    if request.method == "POST":
        a.delete()
        messages.success(request, "Affectation supprimée.")
        return redirect("affectations:list")
    return render(request, "affectations/affectation_confirm_delete.html", {"a": a})


TYPE_MAP = {
    "FONCTION": "FONCTION",
    "AGENCE": "AGENCE",
    "LES_DEUX": "LES_DEUX",
    # on tolère quelques variantes
    "fonction": "FONCTION",
    "agence": "AGENCE",
    "les_deux": "LES_DEUX",
    "fonction_agence": "LES_DEUX",
    "fonction+agence": "LES_DEUX",
}


def affectation_choose_type(request):
    form = ChoixTypeForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        raw = form.cleaned_data["type_affectation"]
        affect_type = TYPE_MAP.get(raw, "FONCTION")  # normalise
        request.session["aff_type"] = affect_type

        # on efface toute sélection précédente d’agents
        for k in ("aff_mat", "aff_mat_list", "aff_mat_index", "aff_candidates"):
            request.session.pop(k, None)

        return redirect("affectations:choose_agent")

    # pré-cocher la valeur courante si déjà en session
    current = request.session.get("aff_type", "FONCTION")
    return render(
        request, "affectations/choose_type.html", {"form": form, "current": current}
    )


def _agent_base(matricule):
    ag = Agent.objects.using("default").filter(Matricule=matricule).first()
    return {
        "Matricule": matricule,
        "Nom": getattr(ag, "Nom", "") if ag else "",
        "Prenom": getattr(ag, "Prenom", "") if ag else "",
        "CodeFonctionAncien": (
            getattr(ag, "FonctionCode", "") if hasattr(ag, "FonctionCode") else ""
        ),
        "LibelleFonctionAncien": (
            getattr(ag, "FonctionLibelle", "") if hasattr(ag, "FonctionLibelle") else ""
        ),
        "CodeEntiteAncien": (
            getattr(ag, "AffectationCode", "") if hasattr(ag, "AffectationCode") else ""
        ),
        "LibelleEntiteAncien": (
            getattr(ag, "AffectationLibelle", "")
            if hasattr(ag, "AffectationLibelle")
            else ""
        ),
    }


def _resolve_current_function_for_agent(matricule: str):
    """
    Retourne (code, libellé) de la fonction ACTUELLE d'un agent
    en se basant sur sa dernière affectation si besoin.
    Règle : on privilégie ...Nouveau, sinon ...Ancien.
    """
    last_aff = (
        Affectation.objects.filter(Matricule=str(matricule))
        .order_by("-DateLettreAffectation", "-DateMobilite", "-NumeroAffectation")
        .first()
    )
    if not last_aff:
        return (None, None)
    code = last_aff.CodeFonctionNouveau or last_aff.CodeFonctionAncien
    lib = last_aff.LibelleFonctionNouveau or last_aff.LibelleFonctionAncien
    return (code, lib)


def affectation_step1(request):
    """
    Étape 1 : Vérification / résumé figé avant saisie.
    Remplit la Partie ANCIENNE :
      - Fonction (Code) et Fonction (Libellé) depuis Agent.FonctionCode / Agent.FonctionLibelle
      - Si absent, fallback sur la dernière Affectation (…Nouveau puis …Ancien)
      - Affectation (Code/Libellé) actuelles depuis Agent
    """
    # 1) Récupération du matricule choisi (mono ou multi-sélection)
    matricule = request.session.get("aff_mat")
    if not matricule:
        lst = request.session.get("aff_mat_list")
        idx = int(request.session.get("aff_mat_index", 0))
        if not lst or idx >= len(lst):
            return redirect("affectations:choose_agent")
        matricule = lst[idx]

    # 2) Agent
    agent = get_object_or_404(Agent.objects.using("default"), Matricule=str(matricule))

    # 3) Fonction ACTUELLE (priorité aux champs de l'agent)
    f_code = getattr(agent, "FonctionCode", None)
    f_lib = getattr(agent, "FonctionLibelle", None)

    # Fallback : déduire depuis la dernière affectation si l'agent n'a pas ces colonnes renseignées
    if not f_code or not f_lib:
        fx_code, fx_lib = _resolve_current_function_for_agent(matricule)
        f_code = f_code or fx_code
        f_lib = f_lib or fx_lib

    # 4) Affectation ACTUELLE (depuis l'agent)
    a_code = getattr(agent, "AffectationCode", "") or ""
    a_lib = getattr(agent, "AffectationLibelle", "") or ""

    # 5) Numéro prévisionnel (ne sera réellement consommé qu'à l'enregistrement)
    preview_num = Affectation.next_numero_for_year()

    # 6) Payload initial pour le formulaire figé
    initial = {
        "NumeroAffectationPreview": preview_num,
        "Matricule": agent.Matricule,
        "Nom": agent.Nom,
        "Prenom": agent.Prenom,
        # Partie ANCIENNE – ce que tu veux voir dans les champs entourés
        "CodeFonctionAncien": f_code or "",
        "LibelleFonctionAncien": f_lib or "",
        "CodeEntiteAncien": a_code,
        "LibelleEntiteAncien": a_lib,
    }

    # 7) Navigation bouton : "Suivant" -> step2 (rien à valider ici)
    if request.method == "POST":
        return redirect("affectations:step2")

    form = AffectationStep1Form(initial=initial)

    # (optionnel) progression si sélection multiple
    progress = None
    if request.session.get("aff_mat_list"):
        progress = {
            "current": int(request.session.get("aff_mat_index", 0)) + 1,
            "total": len(request.session["aff_mat_list"]),
        }

    return render(
        request,
        "affectations/step1.html",
        {
            "form": form,
            "progress": progress,
        },
    )


@transaction.atomic
def affectation_step2(request):
    """
    Étape 2 : saisie des nouvelles infos.
    - Listes déroulantes pour ENTITÉ et FONCTION (code + libellé)
    - Respect du type FONCTION / AGENCE / LES_DEUX
    - Numéro auto 'XXX/AAAA'
    - Gère mono et multi-sélection (aff_mat / aff_mat_list / aff_mat_index)
    """

    # ---------------- helpers ----------------
    def _next_numero_for_year_fallback():
        year = timezone.now().year
        suffix = f"/{year}"
        last = (
            Affectation.objects.using("default")
            .filter(NumeroAffectation__endswith=suffix)
            .values_list("NumeroAffectation", flat=True)
            .order_by("-NumeroAffectation")
            .first()
        )
        n = 0
        if last and "/" in last:
            try:
                n = int(last.split("/")[0])
            except Exception:
                n = 0
        return f"{n+1:03d}/{year}"

    def _get_numero():
        if hasattr(Affectation, "next_numero_for_year") and callable(
            Affectation.next_numero_for_year
        ):
            try:
                return Affectation.next_numero_for_year()
            except Exception:
                pass
        return _next_numero_for_year_fallback()

    def _field(obj, *names):
        """Retourne le premier attribut existant parmi names."""
        for n in names:
            if hasattr(obj, n):
                return getattr(obj, n)
        return ""

    # --------------- état wizard ---------------
    type_aff = request.session.get("aff_type")  # "FONCTION" | "AGENCE" | "LES_DEUX"
    if type_aff not in {"FONCTION", "AGENCE", "LES_DEUX"}:
        messages.error(request, "Type d’affectation non précisé.")
        return redirect("affectations:choose_type")

    mat = request.session.get("aff_mat")
    mat_list = request.session.get("aff_mat_list")
    idx = int(request.session.get("aff_mat_index", 0) or 0)

    if not mat:
        if not mat_list:
            messages.error(request, "Aucun agent sélectionné.")
            return redirect("affectations:choose_type")
        if idx >= len(mat_list):
            return redirect("affectations:list")
        mat = mat_list[idx]

    agent = get_object_or_404(Agent.objects.using("default"), Matricule=str(mat))

    progress = None
    if mat_list:
        progress = {"current": idx + 1, "total": len(mat_list)}

    # --------------- choices ENTITE ---------------
    entites_qs = Entite.objects.using("default").all().order_by("AffectationLibelle")
    ent_choices_code = [("", "— Sélectionner —")] + [
        (e.AffectationCode, f"{e.AffectationCode} — {e.AffectationLibelle}")
        for e in entites_qs
    ]
    ent_choices_lib = [("", "— Sélectionner —")] + [
        (e.AffectationLibelle, e.AffectationLibelle) for e in entites_qs
    ]

    # --------------- choices FONCTION ---------------
    # Tri et extraction robustes quel que soit le nom des colonnes
    fonctions_qs = Fonction.objects.using("default").all()
    try:
        fonctions_qs = fonctions_qs.order_by(
            "Libelle",
            "LibelleFonction",
            "FonctionLibelle",
            "Intitule",
            "IntituleFonction",
            "Designation",
            "Titre",
        )
    except Exception:
        pass

    def _get_attr_any(obj, *names):
        """Retourne la 1re valeur non vide parmi les attributs listés."""
        for n in names:
            if hasattr(obj, n):
                v = getattr(obj, n)
                if v not in (None, ""):
                    return str(v)
        return ""

    fonc_choices_code = [("", "— Sélectionner —")]
    fonc_choices_lib = [("", "— Sélectionner —")]
    seen_libs = set()
    for f in fonctions_qs:
        code = _get_attr_any(f, "Code", "CodeFonction", "FonctionCode").strip()
        lib = _get_attr_any(
            f,
            "Libelle",
            "LibelleFonction",
            "FonctionLibelle",
            "Intitule",
            "IntituleFonction",
            "Designation",
            "Titre",
        ).strip()
        display_lib = lib or code  # au pire on montre le code
        if code or lib:
            fonc_choices_code.append(
                (code, f"{code} — {display_lib}" if code else display_lib)
            )
            if display_lib and display_lib not in seen_libs:
                fonc_choices_lib.append((display_lib, display_lib))
                seen_libs.add(display_lib)

    # --------------- POST ---------------
    if request.method == "POST":
        form = AffectationStep2Form(request.POST)

        # Rendre optionnels les champs non concernés
        if type_aff == "FONCTION":
            for f in ("CodeEntiteNouveau", "LibelleEntiteNouveau"):
                if f in form.fields:
                    form.fields[f].required = False
        elif type_aff == "AGENCE":
            for f in ("CodeFonctionNouveau", "LibelleFonctionNouveau"):
                if f in form.fields:
                    form.fields[f].required = False

        # Injecter ChoiceField ENTITÉ si nécessaire
        if type_aff in {"AGENCE", "LES_DEUX"}:
            if "CodeEntiteNouveau" in form.fields:
                form.fields["CodeEntiteNouveau"] = forms.ChoiceField(
                    choices=ent_choices_code,
                    required=True,
                    widget=forms.Select(attrs={"class": "form-select"}),
                )
            if "LibelleEntiteNouveau" in form.fields:
                form.fields["LibelleEntiteNouveau"] = forms.ChoiceField(
                    choices=ent_choices_lib,
                    required=False,
                    widget=forms.Select(attrs={"class": "form-select"}),
                )

        # Injecter ChoiceField FONCTION si nécessaire
        if type_aff in {"FONCTION", "LES_DEUX"}:
            if "CodeFonctionNouveau" in form.fields:
                form.fields["CodeFonctionNouveau"] = forms.ChoiceField(
                    choices=fonc_choices_code,
                    required=True,
                    widget=forms.Select(attrs={"class": "form-select"}),
                )
            if "LibelleFonctionNouveau" in form.fields:
                form.fields["LibelleFonctionNouveau"] = forms.ChoiceField(
                    choices=fonc_choices_lib,
                    required=False,
                    widget=forms.Select(attrs={"class": "form-select"}),
                )

        if not form.is_valid():
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
            return render(
                request,
                "affectations/step2.html",
                {
                    "form": form,
                    "agent": agent,
                    "type_aff": type_aff,
                    "progress": progress,
                },
            )

        cd = form.cleaned_data
        numero = _get_numero()

        # Partie ANCIENNE (depuis l'agent)
        ancien_f_code = getattr(agent, "FonctionCode", None)
        ancien_f_lib = getattr(agent, "FonctionLibelle", None)
        ancien_e_code = getattr(agent, "AffectationCode", None)
        ancien_e_lib = getattr(agent, "AffectationLibelle", None)

        # Partie NOUVELLE choisie
        new_f_code = (
            cd.get("CodeFonctionNouveau")
            if type_aff in {"FONCTION", "LES_DEUX"}
            else None
        )
        new_f_lib = (
            cd.get("LibelleFonctionNouveau")
            if type_aff in {"FONCTION", "LES_DEUX"}
            else None
        )
        new_e_code = (
            cd.get("CodeEntiteNouveau") if type_aff in {"AGENCE", "LES_DEUX"} else None
        )
        new_e_lib = (
            cd.get("LibelleEntiteNouveau")
            if type_aff in {"AGENCE", "LES_DEUX"}
            else None
        )
        new_arbo = None

        # Auto-compléter ENTITÉ (code -> libellé + arborescence)
        if new_e_code:
            ent = (
                Entite.objects.using("default")
                .filter(AffectationCode=new_e_code)
                .first()
            )
            if ent:
                if not new_e_lib:
                    new_e_lib = getattr(ent, "AffectationLibelle", None)
                new_arbo = getattr(ent, "ArborescenceAffectation", None) or getattr(
                    ent, "Arborescence", None
                )

        # Auto-compléter FONCTION (code <-> libellé)
        if type_aff in {"FONCTION", "LES_DEUX"}:
            if new_f_code and not new_f_lib:
                fobj = (
                    Fonction.objects.using("default")
                    .filter(
                        Q(Code=new_f_code)
                        | Q(CodeFonction=new_f_code)
                        | Q(FonctionCode=new_f_code)
                    )
                    .first()
                )
                if fobj:
                    new_f_lib = _field(
                        fobj,
                        "Libelle",
                        "LibelleFonction",
                        "FonctionLibelle",
                        "Intitule",
                        "IntituleFonction",
                        "Designation",
                        "Titre",
                    )
            elif new_f_lib and not new_f_code:
                fobj = (
                    Fonction.objects.using("default")
                    .filter(
                        Q(Libelle=new_f_lib)
                        | Q(LibelleFonction=new_f_lib)
                        | Q(FonctionLibelle=new_f_lib)
                        | Q(Intitule=new_f_lib)
                        | Q(IntituleFonction=new_f_lib)
                        | Q(Designation=new_f_lib)
                        | Q(Titre=new_f_lib)
                    )
                    .first()
                )
                if fobj:
                    new_f_code = _field(fobj, "Code", "CodeFonction", "FonctionCode")

        flag_f = bool(new_f_code or new_f_lib)
        flag_e = bool(new_e_code or new_e_lib)

        a = Affectation(
            NumeroAffectation=numero,
            DateMobilite=cd.get("DateMobilite"),
            DateLettreAffectation=cd.get("DateLettreAffectation"),
            Matricule=str(agent.Matricule),
            # ancien
            CodeFonctionAncien=ancien_f_code,
            LibelleFonctionAncien=ancien_f_lib,
            DateFonctionAncien=None,
            CodeEntiteAncien=ancien_e_code,
            LibelleEntiteAncien=ancien_e_lib,
            DateAffectationAncien=None,
            # nouveau
            CodeFonctionNouveau=new_f_code,
            LibelleFonctionNouveau=new_f_lib,
            CodeEntiteNouveau=new_e_code,
            LibelleEntiteNouveau=new_e_lib,
            # flags
            ChangementAffectation=flag_e,
            ChangementFonction=flag_f,
        )
        if hasattr(a, "CreatedAt"):
            a.CreatedAt = timezone.now()
        if hasattr(a, "UpdatedAt"):
            a.UpdatedAt = timezone.now()
        a.save(using="default")

        # Mise à jour Agent
        if flag_f:
            if new_f_code:
                agent.FonctionCode = new_f_code
            if new_f_lib:
                agent.FonctionLibelle = new_f_lib
        if flag_e:
            if new_e_code:
                agent.AffectationCode = new_e_code
            if new_e_lib:
                agent.AffectationLibelle = new_e_lib
            if new_arbo and hasattr(agent, "ArborescenceAffectation"):
                agent.ArborescenceAffectation = new_arbo
        agent.save(using="default")

        messages.success(request, f"Affectation {a.NumeroAffectation} enregistrée.")

        # multi : passer au suivant
        if mat_list:
            nxt = idx + 1
            if nxt < len(mat_list):
                request.session["aff_mat_index"] = nxt
                request.session["aff_mat"] = mat_list[nxt]
                return redirect("affectations:step1")
            for k in ("aff_mat", "aff_mat_list", "aff_mat_index"):
                request.session.pop(k, None)
            return redirect("affectations:list")

        # mono : détail si possible
        try:
            return redirect("affectations:detail", pk=a.NumeroAffectation)
        except Exception:
            return redirect("affectations:list")

    # --------------- GET ---------------
    form = AffectationStep2Form()

    # required selon type
    if type_aff == "FONCTION":
        for f in ("CodeEntiteNouveau", "LibelleEntiteNouveau"):
            if f in form.fields:
                form.fields[f].required = False
    elif type_aff == "AGENCE":
        for f in ("CodeFonctionNouveau", "LibelleFonctionNouveau"):
            if f in form.fields:
                form.fields[f].required = False

    # ENTITÉ en select si concerné
    if type_aff in {"AGENCE", "LES_DEUX"}:
        if "CodeEntiteNouveau" in form.fields:
            form.fields["CodeEntiteNouveau"] = forms.ChoiceField(
                choices=ent_choices_code,
                required=True,
                widget=forms.Select(attrs={"class": "form-select"}),
            )
        if "LibelleEntiteNouveau" in form.fields:
            form.fields["LibelleEntiteNouveau"] = forms.ChoiceField(
                choices=ent_choices_lib,
                required=False,
                widget=forms.Select(attrs={"class": "form-select"}),
            )

    # FONCTION en select si concerné
    if type_aff in {"FONCTION", "LES_DEUX"}:
        if "CodeFonctionNouveau" in form.fields:
            form.fields["CodeFonctionNouveau"] = forms.ChoiceField(
                choices=fonc_choices_code,
                required=True,
                widget=forms.Select(attrs={"class": "form-select"}),
            )
        if "LibelleFonctionNouveau" in form.fields:
            form.fields["LibelleFonctionNouveau"] = forms.ChoiceField(
                choices=fonc_choices_lib,
                required=False,
                widget=forms.Select(attrs={"class": "form-select"}),
            )

    return render(
        request,
        "affectations/step2.html",
        {"form": form, "agent": agent, "type_aff": type_aff, "progress": progress},
    )


def _render_html_to_pdf(template_name: str, context: dict, filename: str):
    """Rend un template HTML en PDF (xhtml2pdf). En dev: renvoie le HTML s'il y a une erreur."""
    tpl = get_template(template_name)
    html = tpl.render(context)
    buf = BytesIO()
    result = pisa.CreatePDF(src=html, dest=buf, encoding="utf-8")
    if result.err:
        return HttpResponse(html)  # pratique pour débugger le template
    buf.seek(0)
    resp = HttpResponse(buf, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="{filename}"'
    return resp


def _affectation_context(a, agent=None):
    """Contexte commun pour les 3 modèles PDF (récupère ancien/nouveau)."""
    return {
        "num": getattr(a, "NumeroAffectation", "") or "",
        "date_lettre": getattr(a, "DateLettreAffectation", None),
        "matricule": getattr(a, "Matricule", "") or "",
        "civilite": getattr(agent, "Civilite", "") if agent else "",
        "nom": getattr(agent, "Nom", "") if agent else "",
        "prenom": getattr(agent, "Prenom", "") if agent else "",
        "date_nais": getattr(agent, "DateNaissance", None) if agent else None,
        # Partie ANCIENNE
        "anc_aff_code": getattr(a, "CodeEntiteAncien", "") or "",
        "anc_aff_lib": getattr(a, "LibelleEntiteAncien", "") or "",
        "anc_date_aff": getattr(a, "DateAffectationAncien", None),
        "anc_fct_code": getattr(a, "CodeFonctionAncien", "") or "",
        "anc_fct_lib": getattr(a, "LibelleFonctionAncien", "") or "",
        "anc_date_fct": getattr(a, "DateFonctionAncien", None),
        # Partie NOUVELLE
        "nv_aff_code": getattr(a, "CodeEntiteNouveau", "") or "",
        "nv_aff_lib": getattr(a, "LibelleEntiteNouveau", "") or "",
        "nv_date_aff": getattr(a, "DateAffectationNouveau", None),
        "nv_fct_code": getattr(a, "CodeFonctionNouveau", "") or "",
        "nv_fct_lib": getattr(a, "LibelleFonctionNouveau", "") or "",
        "nv_date_fct": getattr(a, "DateFonctionNouveau", None),
        "arbo": getattr(agent, "ArborescenceAffectation", "") if agent else "",
    }


DOCX_TYPES = {
    "aff1": {
        "label": "Lettre d’affectation — Modèle 1",
        "docx": "Aff1.docx",
        "filename": lambda c: f"Lettre_Affectation_{c['num']}_Aff1.docx",
    },
    "aff2": {
        "label": "Lettre d’affectation — Modèle 2",
        "docx": "Aff2.docx",
        "filename": lambda c: f"Lettre_Affectation_{c['num']}_Aff2.docx",
    },
    "aff3": {
        "label": "Lettre d’affectation — Modèle 3",
        "docx": "Aff3.docx",
        "filename": lambda c: f"Lettre_Affectation_{c['num']}_Aff3.docx",
    },
}


def affectation_pdf(request, pk):
    a = get_object_or_404(Affectation, pk=pk)
    agent = Agent.objects.using("default").filter(Matricule=a.Matricule).first()
    pdf_type = (request.GET.get("type") or "").lower()

    if pdf_type not in PDF_TYPES:
        options = [{"key": k, "label": v["label"]} for k, v in PDF_TYPES.items()]
        return render(
            request, "affectations/pdf_picker.html", {"a": a, "options": options}
        )

    cfg = PDF_TYPES[pdf_type]
    ctx = _affectation_context(a, agent)

    # commun
    ctx.update({"ville": "Tanger", "reseau": ctx.get("arbo")})

    # variations par modèle si tu veux
    if pdf_type == "aff2":
        ctx.update({"sign_gauche_role": "DIRECTEUR PRINCIPAL CAPITAL HUMAIN"})
    elif pdf_type == "aff3":
        ctx.update({"sign_droite_role": "PRÉSIDENT DU DIRECTOIRE"})

    return _render_html_to_pdf(
        cfg["template"], {"aff": ctx, **ctx}, cfg["filename"](ctx)
    )


def _current_matricule_from_session(request):
    if request.session.get("aff_mat"):
        return request.session["aff_mat"]
    lst = request.session.get("aff_mat_list")
    idx = request.session.get("aff_mat_index")
    if isinstance(lst, list) and isinstance(idx, int) and 0 <= idx < len(lst):
        return lst[idx]
    return None


def _wizard_progress(request):
    """Retourne (current, total) ou (None, None) en mode simple."""
    lst = request.session.get("aff_mat_list")
    idx = request.session.get("aff_mat_index")
    if isinstance(lst, list) and isinstance(idx, int) and lst:
        return idx + 1, len(lst)
    return None, None
