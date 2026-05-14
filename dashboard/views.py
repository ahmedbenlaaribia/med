from datetime import date

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
            messages.success(request, "Le statut du compte a ete mis a jour.")
        elif action == "delete" and not (user.is_staff or user.is_superuser):
            user.delete()
            messages.success(request, "L'utilisateur a ete supprime.")
        else:
            messages.error(request, "Action non autorisee.")
        return redirect("admin_dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        appointments = RendezVous.objects.select_related("medecin__user", "medecin__specialite", "patient")
        total_appointments = appointments.count()
        total_doctors = Medecin.objects.count()
        today = date.today()

        status_counts = {
            "en_attente": appointments.filter(statut="en_attente").count(),
            "confirme": appointments.filter(statut="confirme").count(),
            "termine": appointments.filter(statut="termine").count(),
            "annule": appointments.filter(statut="annule").count(),
        }
        specialty_counts = list(
            appointments.values("medecin__specialite__nom")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        doctor_load = list(
            appointments.values(
                "medecin__user__first_name",
                "medecin__user__last_name",
                "medecin__user__username",
            )
            .annotate(total=Count("id"))
            .order_by("-total")[:5]
        )
        recent_appointments = appointments.order_by("-created_at")[:6]
        for item in doctor_load:
            full_name = " ".join(
                part for part in [item["medecin__user__first_name"], item["medecin__user__last_name"]] if part
            ).strip()
            item["display_name"] = full_name or item["medecin__user__username"]

        context.update(
            {
                "total_patients": User.objects.filter(is_patient=True).count(),
                "total_doctors": total_doctors,
                "validated_doctors": Medecin.objects.filter(is_validated=True).count(),
                "active_users": User.objects.filter(is_active=True).count(),
                "total_appointments": total_appointments,
                "today_appointments": appointments.filter(date=today).count(),
                "appointments_by_specialty": specialty_counts,
                "appointments_by_status": status_counts,
                "doctor_load": doctor_load,
                "recent_appointments": recent_appointments,
                "users_list": User.objects.order_by("-date_joined"),
                "appointments_average_per_doctor": round(total_appointments / total_doctors, 1) if total_doctors else 0,
            }
        )
        return context
