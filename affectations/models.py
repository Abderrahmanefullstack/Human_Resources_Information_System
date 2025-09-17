from django.db import models
from django.utils import timezone


class Affectation(models.Model):
    NumeroAffectation = models.CharField(primary_key=True, max_length=16)

    DateMobilite = models.DateField()
    DateLettreAffectation = models.DateField(null=True, blank=True)

    Matricule = models.CharField(max_length=50)

    # Partie ANCIENNE
    CodeFonctionAncien = models.CharField(max_length=50, null=True, blank=True)
    LibelleFonctionAncien = models.CharField(max_length=150, null=True, blank=True)
    DateFonctionAncien = models.DateField(null=True, blank=True)

    CodeEntiteAncien = models.CharField(max_length=10, null=True, blank=True)
    LibelleEntiteAncien = models.CharField(max_length=100, null=True, blank=True)
    DateAffectationAncien = models.DateField(null=True, blank=True)

    # Partie NOUVELLE
    CodeFonctionNouveau = models.CharField(max_length=50, null=True, blank=True)
    LibelleFonctionNouveau = models.CharField(max_length=150, null=True, blank=True)
    CodeEntiteNouveau = models.CharField(max_length=10, null=True, blank=True)
    LibelleEntiteNouveau = models.CharField(max_length=100, null=True, blank=True)

    # Flags
    ChangementAffectation = models.BooleanField(default=False)
    ChangementFonction = models.BooleanField(default=False)

    CreatedAt = models.DateTimeField(auto_now_add=True, db_column="CreatedAt")
    UpdatedAt = models.DateTimeField(auto_now=True, db_column="UpdatedAt")

    class Meta:
        managed = False  # 🔒 la table existe déjà en SQL
        db_table = "Affectation"
        # pas de CreatedAt/UpdatedAt ici, donc on n’ordonne pas dessus
        ordering = ["-DateLettreAffectation", "-NumeroAffectation"]

    def __str__(self):
        return self.NumeroAffectation

    @staticmethod
    def next_numero_for_year(year=None):
        if year is None:
            year = timezone.now().year
        qs = Affectation.objects.filter(NumeroAffectation__endswith=f"/{year}")
        if not qs.exists():
            return f"001/{year}"
        maxi = 0
        for num in qs.values_list("NumeroAffectation", flat=True):
            try:
                maxi = max(maxi, int(num.split("/")[0]))
            except Exception:
                pass
        return f"{str(maxi+1).zfill(3)}/{year}"
