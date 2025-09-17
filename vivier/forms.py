# -*- coding: utf-8 -*-
from __future__ import annotations
from django import forms
from django.utils import timezone
from .models import Vivier, Commission, PieceJointe
from .utils import build_direction_choices_from_agents, get_fonction_cible_choices
import logging

logger = logging.getLogger(__name__)


class VivierAgenceForm(forms.ModelForm):
    NumCommissionPreview = forms.CharField(
        label="N° Vivier (aperçu)",
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    DateCreation = forms.DateField(
        label="Date",
        initial=lambda: timezone.localdate(),
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=True,
    )
    FonctionCible = forms.ChoiceField(
        label="Fonction cible",
        choices=get_fonction_cible_choices(),
        widget=forms.Select(attrs={"class": "form-select"}),
        required=True,
    )
    DirectionReseau = forms.ChoiceField(
        label="Direction / Réseau",
        choices=build_direction_choices_from_agents,
        widget=forms.Select(attrs={"class": "form-select"}),
        required=True,
    )
    Valide = forms.BooleanField(
        label="Validé",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    DateValidation = forms.DateField(
        label="Date de validation",
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    class Meta:
        model = Vivier
        fields = [
            "DateCreation",
            "FonctionCible",
            "DirectionReseau",
            "Valide",
            "DateValidation",
            "Observation",
        ]
        widgets = {
            "Observation": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean(self):
        cd = super().clean()
        if not cd.get("Valide"):
            cd["DateValidation"] = None
        return cd


class VivierCreateForm(forms.ModelForm):
    FonctionCible = forms.ChoiceField(
        choices=get_fonction_cible_choices(), required=True, label="Fonction cible"
    )
    DirectionReseau = forms.ChoiceField(
        choices=[], required=True, label="Direction / Réseau"
    )

    class Meta:
        model = Vivier
        fields = ["NumCommission", "DateCreation", "FonctionCible", "DirectionReseau"]
        widgets = {
            "NumCommission": forms.TextInput(
                attrs={"class": "form-control", "readonly": True}
            ),
            "DateCreation": forms.DateInput(
                attrs={"type": "date", "class": "form-control", "required": True}
            ),
            "FonctionCible": forms.Select(
                attrs={"class": "form-select", "required": True}
            ),
            "DirectionReseau": forms.Select(
                attrs={"class": "form-select", "required": True}
            ),
        }
        labels = {"NumCommission": "N° vivier", "DateCreation": "Date"}

    def __init__(self, *args, direction_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        if direction_choices is None:
            direction_choices = build_direction_choices_from_agents()
        self.fields["DirectionReseau"].choices = direction_choices


class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultiFileField(forms.FileField):
    """Accepte 0..n fichiers sans déclencher l'erreur 'No file was submitted'."""

    def to_python(self, data):
        if data in self.empty_values:
            return []
        if isinstance(data, (list, tuple)):
            # Si le navigateur envoie déjà une liste, on la garde
            return list(data)
        # Sinon, un seul fichier -> on le met dans une liste
        return [super().to_python(data)]


class VivierUpdateForm(forms.ModelForm):
    """
    Uniquement pour la zone 'Compléments' de la page Modifier.
    On ne touche qu'à Observation et pièces jointes.
    """

    pieces = MultiFileField(
        required=False,
        label="Pièces jointes",
        widget=MultiFileInput(attrs={"multiple": True}),
    )

    class Meta:
        model = Vivier
        fields = ["Observation"]
        widgets = {
            "Observation": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {"Observation": "Observation"}

    def clean_pieces(self):
        files = self.files.getlist(self.add_prefix("pieces"))
        for f in files:
            if f.size > 20 * 1024 * 1024:
                raise forms.ValidationError(
                    "Chaque pièce jointe ne doit pas dépasser 20 Mo."
                )
        return files

    def save(self, commit=True):
        vivier = super().save(commit=commit)
        files = self.files.getlist(self.add_prefix("pieces"))
        for f in files:
            data = f.read()
            PieceJointe.objects.create(
                vivier=vivier,
                nom=f.name,
                mime=getattr(f, "content_type", "") or "",
                taille=f.size,
                data=data,
            )
        return vivier


class VivierPiecesForm(forms.Form):
    pieces = forms.FileField(
        widget=MultiFileInput(attrs={"multiple": True}),
        required=False,
        label="Pièces jointes",
    )


class VivierValidationForm(forms.ModelForm):
    class Meta:
        model = Vivier
        fields = ["Valide", "DateValidation"]
        widgets = {
            "Valide": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "DateValidation": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }
        labels = {"Valide": "Validé", "DateValidation": "Date de validation"}

    def clean(self):
        cd = super().clean()
        if not cd.get("Valide"):
            cd["DateValidation"] = None
        else:
            if not cd.get("DateValidation"):
                self.add_error("DateValidation", "Obligatoire si 'Validé' est coché.")
        return cd


DECISION_CHOICES = [
    ("", "— Sélectionner —"),
    ("RETENU", "Retenu(e)"),
    ("NON_RETENU", "Non retenu(e)"),
    ("ABSENT", "Absent(e)"),
    ("DESISTEMENT", "Désistement"),
]


class CommissionForm(forms.ModelForm):
    class Meta:
        model = Commission
        fields = [
            "Sanction",
            "PI_n_1",
            "PI_n_2",
            "PI_n_3",
            "AvisCommission",
            "Note",
            "Decision",
            "MotifDecision",
            "Caractere",
        ]
        widgets = {
            "Sanction": forms.TextInput(attrs={"class": "form-control"}),
            "PI_n_1": forms.TextInput(attrs={"class": "form-control"}),
            "PI_n_2": forms.TextInput(attrs={"class": "form-control"}),
            "PI_n_3": forms.TextInput(attrs={"class": "form-control"}),
            "AvisCommission": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "Note": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "Decision": forms.Select(
                attrs={"class": "form-select"}, choices=DECISION_CHOICES
            ),
            "MotifDecision": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "Caractere": forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "Sanction": "Sanction",
            "PI_n_1": "PI n-1",
            "PI_n_2": "PI n-2",
            "PI_n_3": "PI n-3",
            "AvisCommission": "Avis de la commission",
            "Note": "Note",
            "Decision": "Décision",
            "MotifDecision": "Motif décision",
            "Caractere": "Caractère",
        }

    def clean_Note(self):
        v = self.cleaned_data.get("Note")
        if isinstance(v, str):
            v = v.replace(",", ".")
        return v
