from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView

from appointments.models import RendezVous
from doctors.models import Medecin


class AdminDashboardView(UserPassesTestMixin, TemplateView):
    template_name = "dashboard/admin_dashboard.html"

    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_staff or self.request.user.is_superuser
        )

    def handle_no_permission(self):
        return redirect("home")

    def post(self, request, *args, **kwargs):
        User = get_user_model()
        action = request.POST.get("action")
        user = get_object_or_404(User, pk=request.POST.get("user_id"))

        if user == request.user:
            messages.error(request, "Vous ne pouvez pas modifier votre propre compte depuis ce tableau.")
            return redirect("admin_dashboard")

        if action == "toggle_active":
            user.is_active = not user.is_active
            user.save(update_fields=["is_active"])
            messages.success(request, "Le statut du compte a été mis à jour.")
        elif action == "delete" and not (user.is_staff or user.is_superuser):
            user.delete()
            messages.success(request, "L'utilisateur a été supprimé.")
        else:
            messages.error(request, "Action non autorisée.")
        return redirect("admin_dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        specialty_counts = (
            RendezVous.objects.values("medecin__specialite__nom")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        context["total_patients"] = User.objects.filter(is_patient=True).count()
        context["total_doctors"] = Medecin.objects.count()
        context["total_appointments"] = RendezVous.objects.count()
        context["appointments_by_specialty"] = specialty_counts
        context["most_requested_specialties"] = specialty_counts[:5]
        context["users_list"] = User.objects.order_by("-date_joined")
        return context
