# vivier/admin.py
from django.contrib import admin
from .models import Vivier, Commission


@admin.register(Vivier)
class VivierAdmin(admin.ModelAdmin):
    list_display = (
        "NumCommission",
        "DateCreation",
        "FonctionCible",
        "DirectionReseau",
        "Valide",
        "DateValidation",
    )
    search_fields = ("NumCommission", "FonctionCible", "DirectionReseau")
    list_filter = ("Valide", "FonctionCible", "DirectionReseau")


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = (
        "get_num_commission",  # au lieu d'un champ incertain
        "Matricule",
        "Trajectoire",
        "Sanction",
        "get_pi_n1",  # remplace "PI_n1"
        "get_pi_n2",  # remplace "PI_n2"
        "get_pi_n3",  # remplace "PI_n3"
        "AvisCommission",
        "Decision",
        "Note",
        "MotifDecision",
        "Caractere",
    )
    search_fields = ("Matricule",)
    list_filter = ("Trajectoire", "Decision", "Sanction")

    # ---------- helpers robustes ----------
    def get_num_commission(self, obj):
        """
        Retourne le N° Commission :
        - d'abord un champ texte direct dans Commission (NumeroCommission / NumCommission)
        - sinon via un FK 'vivier' → vivier.NumCommission
        """
        direct = getattr(obj, "NumeroCommission", None) or getattr(
            obj, "NumCommission", None
        )
        if direct:
            return direct
        # Essai FK
        ref = getattr(obj, "vivier", None) or getattr(obj, "Vivier", None)
        if ref and hasattr(ref, "NumCommission"):
            return ref.NumCommission
        return "—"

    get_num_commission.short_description = "N° Commission"

    def _get_first_attr(self, obj, *names):
        """Prend la première valeur non vide parmi les attributs donnés."""
        for n in names:
            if hasattr(obj, n):
                v = getattr(obj, n)
                if v not in (None, ""):
                    return v
        return None

    # PI n-1 / n-2 / n-3 avec fallback de noms
    def get_pi_n1(self, obj):
        return self._get_first_attr(
            obj, "PI_n1", "PI_n_1", "PI1", "PiN1", "PI_N1", "PI_n_01"
        )

    get_pi_n1.short_description = "PI n-1"

    def get_pi_n2(self, obj):
        return self._get_first_attr(
            obj, "PI_n2", "PI_n_2", "PI2", "PiN2", "PI_N2", "PI_n_02"
        )

    get_pi_n2.short_description = "PI n-2"

    def get_pi_n3(self, obj):
        return self._get_first_attr(
            obj, "PI_n3", "PI_n_3", "PI3", "PiN3", "PI_N3", "PI_n_03"
        )

    get_pi_n3.short_description = "PI n-3"
