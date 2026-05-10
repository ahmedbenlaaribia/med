from django.contrib import admin

from .models import DateBloquee, Disponibilite, Medecin, Specialite


@admin.register(Specialite)
class SpecialiteAdmin(admin.ModelAdmin):
    list_display = ("nom", "slug")
    search_fields = ("nom",)
    prepopulated_fields = {"slug": ("nom",)}


@admin.register(Medecin)
class MedecinAdmin(admin.ModelAdmin):
    list_display = ("user", "specialite", "ville", "tarif", "is_validated")
    list_filter = ("specialite", "ville", "is_validated")
    search_fields = ("user__first_name", "user__last_name", "user__username", "ville")


@admin.register(Disponibilite)
class DisponibiliteAdmin(admin.ModelAdmin):
    list_display = ("medecin", "jour", "heure_debut", "heure_fin")
    list_filter = ("jour",)


@admin.register(DateBloquee)
class DateBloqueeAdmin(admin.ModelAdmin):
    list_display = ("medecin", "date", "motif")
    list_filter = ("date",)
