from django import forms
from .models import Fonction


class FonctionForm(forms.ModelForm):
    class Meta:
        model = Fonction
        fields = ["Code", "Intitule", "Intitule_Complet"]
        widgets = {
            "Code": forms.TextInput(attrs={"class": "form-control"}),
            "Intitule": forms.TextInput(attrs={"class": "form-control"}),
            "Intitule_Complet": forms.TextInput(attrs={"class": "form-control"}),
        }
