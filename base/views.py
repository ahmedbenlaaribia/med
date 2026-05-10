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
