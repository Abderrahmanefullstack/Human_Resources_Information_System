from django import forms
from .models import AnnonceRH


class AnnonceRHForm(forms.ModelForm):
    # on force le widget HTML5 + on précise le format attendu
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"],
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"],
    )

    class Meta:
        model = AnnonceRH
        fields = ["titre", "contenu", "date_debut", "date_fin", "actif"]
