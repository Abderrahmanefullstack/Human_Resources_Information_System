# affectations/forms.py
from django import forms
from .models import Affectation

# --- Choix du type d'affectation
CHOIX_TYPE = (
    ("FONCTION", "Affectation de Fonction"),
    ("AGENCE", "Affectation d’Agence"),
    ("LES_DEUX", "Fonction + Agence"),
)


class ChoixTypeForm(forms.Form):
    type_affectation = forms.ChoiceField(
        label="Type d’affectation", choices=CHOIX_TYPE, widget=forms.RadioSelect
    )


# --- Recherche / sélection d’agents (liste des agents)
class ChoixAgentForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "🔎 Matricule, nom, prénom",
                "class": "form-control",
            }
        ),
    )


# --- Step 1 : info récap figée
class AffectationStep1Form(forms.Form):
    NumeroAffectationPreview = forms.CharField(
        disabled=True, required=False, label="N° Affectation"
    )
    Matricule = forms.CharField(disabled=True, required=False)
    Nom = forms.CharField(disabled=True, required=False)
    Prenom = forms.CharField(disabled=True, required=False)

    CodeFonctionAncien = forms.CharField(
        disabled=True, required=False, label="Fonction (Code) – Ancien"
    )
    LibelleFonctionAncien = forms.CharField(
        disabled=True, required=False, label="Fonction (Libellé) – Ancien"
    )
    CodeEntiteAncien = forms.CharField(
        disabled=True, required=False, label="Affectation (Code) – Ancien"
    )
    LibelleEntiteAncien = forms.CharField(
        disabled=True, required=False, label="Affectation (Libellé) – Ancien"
    )


# --- Step 2 : saisie des nouvelles infos (aligné modèle/DB)
class AffectationStep2Form(forms.ModelForm):
    class Meta:
        model = Affectation
        fields = [
            "DateMobilite",
            "DateLettreAffectation",
            "CodeFonctionNouveau",
            "LibelleFonctionNouveau",
            "CodeEntiteNouveau",
            "LibelleEntiteNouveau",
        ]
        widgets = {
            "DateMobilite": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "DateLettreAffectation": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "CodeFonctionNouveau": forms.TextInput(attrs={"class": "form-control"}),
            "LibelleFonctionNouveau": forms.TextInput(attrs={"class": "form-control"}),
            "CodeEntiteNouveau": forms.TextInput(attrs={"class": "form-control"}),
            "LibelleEntiteNouveau": forms.TextInput(attrs={"class": "form-control"}),
        }
