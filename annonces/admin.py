from django.contrib import admin
from .models import AnnonceRH


@admin.register(AnnonceRH)
class AnnonceRHAdmin(admin.ModelAdmin):
    list_display = ("titre", "actif", "date_debut", "date_fin", "created_at")
    list_filter = ("actif",)
    search_fields = ("titre", "contenu")
    ordering = ("-created_at",)
