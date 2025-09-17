from django import forms
from .models import Entite


class EntiteForm(forms.ModelForm):
    class Meta:
        model = Entite
        fields = "__all__"
        widgets = {
            "AffectationCode": forms.TextInput(
                attrs={"placeholder": " ", "class": "form-control"}
            ),
            "AffectationLibelle": forms.TextInput(
                attrs={"placeholder": " ", "class": "form-control"}
            ),
            "ArborescenceAffectation": forms.TextInput(
                attrs={"placeholder": " ", "class": "form-control"}
            ),
        }
