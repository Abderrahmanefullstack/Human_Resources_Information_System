from django.db import models


class Entite(models.Model):
    AffectationCode = models.CharField(max_length=10, primary_key=True)
    AffectationLibelle = models.CharField(max_length=100)
    ArborescenceAffectation = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "Entite"
        app_label = "entites"

    @property
    def affectationCode_formate(self):
        """Retourne le matricule sur 10 chiffres avec des zéros à gauche."""
        if self.AffectationCode:
            return str(self.AffectationCode).zfill(6)
        return ""
