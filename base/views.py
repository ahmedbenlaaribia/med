from django.urls import reverse
from django.views.generic import TemplateView

from appointments.models import RendezVous
from doctors.models import Medecin, Specialite


class HomeView(TemplateView):
    template_name = "base/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stats"] = {
            "specialites": Specialite.objects.count(),
            "medecins": Medecin.objects.filter(is_validated=True).count(),
            "rendez_vous": RendezVous.objects.count(),
        }
        context["steps"] = [
            {
                "icon": "fa-user-plus",
                "title": "Creer un compte",
                "description": "Inscrivez-vous en tant que patient puis connectez-vous a votre espace personnel.",
            },
            {
                "icon": "fa-user-doctor",
                "title": "Choisir un medecin",
                "description": "Parcourez les profils verifies, comparez les specialites et consultez les disponibilites.",
            },
            {
                "icon": "fa-calendar-check",
                "title": "Reserver un creneau",
                "description": "Selectionnez un horaire libre et confirmez votre demande de rendez-vous en quelques secondes.",
            },
        ]
        context["features"] = [
            {
                "icon": "fa-filter",
                "title": "Recherche simple",
                "description": "Filtrez par ville, specialite ou nom pour trouver rapidement le bon praticien.",
            },
            {
                "icon": "fa-clock",
                "title": "Disponibilites claires",
                "description": "Visualisez les creneaux libres et les dates bloquees sans appel telephonique.",
            },
            {
                "icon": "fa-clipboard-list",
                "title": "Suivi des rendez-vous",
                "description": "Consultez vos rendez-vous a venir, votre historique et l'etat de chaque demande.",
            },
            {
                "icon": "fa-chart-column",
                "title": "Pilotage admin",
                "description": "L'administration suit les indicateurs globaux de la plateforme avec des statistiques utiles.",
            },
        ]
        user = self.request.user
        dashboard_url = None
        if user.is_authenticated:
            if user.is_staff or user.is_superuser:
                dashboard_url = reverse("admin_dashboard")
            elif user.is_doctor:
                dashboard_url = reverse("doctor_dashboard")
            elif user.is_patient:
                dashboard_url = reverse("patient_appointments")
        context["dashboard_url"] = dashboard_url
        return context
