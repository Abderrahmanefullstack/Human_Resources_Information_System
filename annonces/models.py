from django.db import models
from django.utils import timezone


class AnnonceRH(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    actif = models.BooleanField(default=True)  # ✅ important

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

    @property
    def est_visible(self):
        today = timezone.localdate()
        if not self.actif:
            return False
        if self.date_debut and self.date_debut > today:
            return False
        if self.date_fin and self.date_fin < today:
            return False
        return True
