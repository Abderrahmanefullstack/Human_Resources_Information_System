# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from agents.models import Agent

# from .utils import trajectoire_respectee_agence, trajectoire_ok, old_enough


class Vivier(models.Model):
    NumCommission = models.CharField(
        max_length=9,  # "001/2025" -> 8, on garde 9 pour marge
        unique=True,
        verbose_name="Num Commission",
        help_text="Format: 001/2025",
    )
    DateCreation = models.DateField()
    FonctionCible = models.CharField(max_length=120)
    DirectionReseau = models.CharField(max_length=120, blank=True, null=True)
    Valide = models.BooleanField(default=False)
    DateValidation = models.DateField(blank=True, null=True)
    Observation = models.TextField(blank=True, null=True)

    # Ancienne gestion pièce jointe (optionnelle)
    PJ_name = models.CharField(max_length=255, blank=True, null=True)
    PJ_mime = models.CharField(max_length=100, blank=True, null=True)
    PJ_size = models.IntegerField(blank=True, null=True)
    PJ_data = models.BinaryField(blank=True, null=True)

    class Meta:
        db_table = "Vivier"
        app_label = "vivier"
        managed = True

    def has_pj(self) -> bool:
        return bool(self.PJ_data)

    def __str__(self):
        return self.NumCommission


class PieceJointe(models.Model):
    """
    Chaque Vivier peut avoir plusieurs pièces jointes stockées dans la BDD (SQL Server)
    """

    vivier = models.ForeignKey(Vivier, on_delete=models.CASCADE, related_name="pieces")
    nom = models.CharField(max_length=255, blank=True)
    mime = models.CharField(max_length=100, blank=True)
    taille = models.PositiveIntegerField(null=True, blank=True)
    data = models.BinaryField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "PieceJointe"
        app_label = "vivier"
        managed = True

    def __str__(self):
        return self.nom or f"Fichier {self.pk}"


class Commission(models.Model):
    Vivier = models.ForeignKey(
        Vivier,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    Matricule = models.CharField(max_length=50)  # on évite FK si Agent.managed=False
    Trajectoire = models.BooleanField(default=False)
    Sanction = models.CharField(max_length=120, blank=True, null=True)
    PI_n_1 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    PI_n_2 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    PI_n_3 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    AvisCommission = models.CharField(max_length=255, blank=True, null=True)
    Decision = models.CharField(max_length=255, blank=True, null=True)
    Note = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    MotifDecision = models.TextField(blank=True, null=True)
    Caractere = models.CharField(max_length=120, blank=True, null=True)

    class Meta:
        db_table = "Commission"
        app_label = "vivier"
        managed = True

    def save(self, *args, **kwargs):
        # Auto-calcul Trajectoire si non renseigné
        if self.Trajectoire is None and self.Vivier_id and self.Matricule:
            try:
                ag = Agent.objects.using("default").get(Matricule=str(self.Matricule))
                ok_traj = trajectoire_ok(
                    self.Vivier.FonctionCible, ag.FonctionLibelle or ""
                )
                ok_tenure = old_enough(getattr(ag, "DateEffetFonction", None))
                self.Trajectoire = bool(ok_traj and ok_tenure)
            except Agent.DoesNotExist:
                # on laisse Trajectoire à None si on ne retrouve pas l’agent
                pass

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.Vivier_id} - {self.Matricule}"
