# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import unicodedata
from datetime import date
from django.utils import timezone
from agents.models import Agent


# ============ Normalisation ============


def _norm(s: str) -> str:
    """
    Normalise pour comparaison:
    - upper
    - enlève accents
    - compresse espaces
    - harmonise quelques variantes ('PART/PRO' vs 'PAR/PRO', apostrophes)
    """
    s = (s or "").strip().upper()
    s = s.replace("D’", "D'")  # apostrophe courbe -> droite
    s = s.replace("PART/PRO", "PAR/PRO")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"\s+", " ", s)
    return s


def _ok_3ans(d):
    """Ancienneté >= 3 ans à partir de DateEffetFonction."""
    if not d:
        return False
    try:
        d0 = d if isinstance(d, date) else d.date()
    except Exception:
        return False
    return (timezone.localdate() - d0).days >= 3 * 365  # approximation simple


# ============ Règles Trajectoire (selon ce que TU as défini) ============

# On stocke les règles avec des clés "canon" (libellé exact que TU utilises en UI)
# et on garde en interne une version normalisée pour comparer sans erreurs.
FONCTION_CIBLE_CANON = [
    "Conseiller commercial junior",
    "Conseiller commercial senior",
    "Chargé de la clientèle Part/Pro",
    "Directeur d’agence",
]

# mapping: clé normalisée -> libellé canon
_CANON_BY_NORM = {_norm(k): k for k in FONCTION_CIBLE_CANON}

# Règles: pour chaque cible (clé normalisée), set() de libellés autorisés / exceptionnels (normalisés).
_RULES_ALLOW: dict[str, set[str]] = {}
_RULES_EXCEPT: dict[str, set[str]] = {}


def _S(*items: str) -> set[str]:
    return {_norm(x) for x in items}


# 1) CCJ
_RULES_ALLOW[_norm("Conseiller commercial junior")] = _S(
    "Agent Commercial 1", "Agent Commercial 2", "Agent Commercial 3"
)
_RULES_EXCEPT[_norm("Conseiller commercial junior")] = _S(
    # aucune exception
)

# 2) CCS
_RULES_ALLOW[_norm("Conseiller commercial senior")] = _S(
    "Conseiller Commercial Junior 2",
    "Agent Commercial 2",
    "Conseiller Développement Commercial 1",
    "Conseiller Commercial Junior 3",
    "Agent Commercial 3",
    "Conseiller Développement Commercial 2",
)
_RULES_EXCEPT[_norm("Conseiller commercial senior")] = _S(
    "Conseiller Commercial 1",
)

# 3) Directeur d’agence
_RULES_ALLOW[_norm("Directeur d’agence")] = _S(
    "Conseiller Commercial Senior 4",
    "Conseiller Commercial Senior 3",
    "Support administratif 2",
    "Chargé de la clientèle Part/Pro 2",
    "Chargé de la clientèle Part/Pro 3",
)
_RULES_EXCEPT[_norm("Directeur d’agence")] = _S(
    "Conseiller Commercial Senior 1",
    "Conseiller Commercial Senior 2",
    "Chargé de la clientèle Part/Pro 1",
)

# 4) Chargé de la clientèle Part/Pro
_RULES_ALLOW[_norm("Chargé de la clientèle Part/Pro")] = _S(
    "Conseiller Commercial Senior 4",
    "Conseiller Commercial Senior 3",
    "Conseiller Commercial Junior 3",
    "Agent Commercial 2",
)
_RULES_EXCEPT[_norm("Chargé de la clientèle Part/Pro")] = _S(
    "Conseiller Commercial Senior 1",
    "Conseiller Commercial Senior 2",
    "Conseiller Commercial Junior 1",
    "Conseiller Commercial Junior 2",
)


def get_fonction_cible_choices() -> list[tuple[str, str]]:
    """Choices pour les <select> (libellés *canon* dans l’ordre donné)."""
    return [("", "— Sélectionner —")] + [(lbl, lbl) for lbl in FONCTION_CIBLE_CANON]


# ============ Calcul des éligibles (Oui / Non; autres exclus) ============


def compute_eligibles_agence(fonction_cible: str) -> list[dict]:
    """
    Retourne **uniquement** les agents pertinents:
      - 'trajectoire' = True  si >=3 ans et fonction actuelle ∈ ALLOW
      - 'exception'   = True  si >=3 ans et fonction actuelle ∈ EXCEPT
      - sinon: exclu (non retourné)
    Chaque entrée: {"agent": Agent, "trajectoire": bool, "exception": bool}
    """
    cible_norm = _norm(fonction_cible)
    allow = _RULES_ALLOW.get(cible_norm, set())
    excepts = _RULES_EXCEPT.get(cible_norm, set())

    out: list[dict] = []
    for ag in Agent.objects.using("default").all():
        # Ancienneté
        if not _ok_3ans(getattr(ag, "DateEffetFonction", None)):
            continue

        cur_label_norm = _norm(getattr(ag, "FonctionLibelle", "") or "")
        if cur_label_norm in allow:
            out.append({"agent": ag, "trajectoire": True, "exception": False})
        elif cur_label_norm in excepts:
            out.append({"agent": ag, "trajectoire": False, "exception": True})
        else:
            # exclu
            pass

    return out


# ============ Direction / Réseau (depuis Arborescence) ============


def extract_direction_from_arbo(arbo: str) -> str:
    """
    Extrait, depuis une arborescence Agent, le segment Direction/Réseau commençant par
    06462? ou 06463? (où ? ∈ [0..4]) jusqu’au prochain ‘;’.
    """
    if not arbo:
        return ""
    s = str(arbo)

    # Cas strict
    m = re.search(r"(0646(?:2|3)[0-4][^;]*);", s)
    if m:
        return m.group(1).strip()

    # Filet de sécurité
    m = re.search(r"(0646(?:2|3)\d?[^;]*);", s)
    if m:
        return m.group(1).strip()

    return ""


def extract_directions_from_agents() -> list[str]:
    vals = (
        Agent.objects.using("default")
        .exclude(ArborescenceAffectation__isnull=True)
        .exclude(ArborescenceAffectation__exact="")
        .values_list("ArborescenceAffectation", flat=True)
    )
    seen = set()
    for arbo in vals:
        seg = extract_direction_from_arbo(arbo)
        if seg:
            seen.add(seg)
    return sorted(seen)


def build_direction_choices_from_agents() -> list[tuple[str, str]]:
    out = [(d, d) for d in extract_directions_from_agents()]
    return [("", "— Sélectionner —")] + out


# ============ Numéro 'NNN/AAAA' pour Vivier ============


def next_num_for_year(model_cls, year: int) -> str:
    suffix = f"/{year}"
    last = (
        model_cls.objects.using("default")
        .filter(NumCommission__endswith=suffix)
        .values_list("NumCommission", flat=True)
        .order_by("-NumCommission")
        .first()
    )
    n = 0
    if last and "/" in last:
        try:
            n = int(last.split("/")[0])
        except Exception:
            n = 0
    return f"{n+1:03d}/{year}"
