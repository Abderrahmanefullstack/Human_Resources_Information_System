from django import forms
from .models import Agent


class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = [
            "Matricule",
            "Civilite",
            "Nom",
            "Prenom",
            "NoAffiliationCNSS",
            "DateEntree",
            "SituationEffectifLibelle",
            "AffectationCode",
            "AffectationLibelle",
            "ArborescenceAffectation",
        ]  # Ajoute ici les champs modifiables
        widgets = {
            "Matricule": forms.TextInput(
                attrs={"readonly": "readonly"}
            ),  # Empêche modification du matricule si tu veux
        }


class ExcelUploadForm(forms.Form):
    file = forms.FileField(label="Fichier Excel", required=True)
