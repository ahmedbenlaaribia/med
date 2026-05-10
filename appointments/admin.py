from django.contrib import admin

from .models import RendezVous


@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ("patient", "medecin", "date", "heure", "statut")
    list_filter = ("statut", "date", "medecin__specialite")
    search_fields = (
        "patient__username",
        "patient__first_name",
        "patient__last_name",
        "medecin__user__first_name",
        "medecin__user__last_name",
    )
