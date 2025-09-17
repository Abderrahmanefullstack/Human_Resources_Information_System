from django.db import models


class Fonction(models.Model):
    Code = models.CharField(max_length=50, primary_key=True)
    Intitule = models.CharField(max_length=200)
    Intitule_Complet = models.CharField(max_length=300)

    class Meta:
        db_table = "Fonction"
        app_label = "fonctions"
        managed = False  # table existante
