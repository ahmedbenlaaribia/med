from collections import Counter
from datetime import date, timedelta

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from appointments.models import RendezVous
from users.mixins import DoctorRequiredMixin

from .forms import DateBloqueeForm, DisponibiliteForm
from .models import DateBloquee, Disponibilite, Medecin, Specialite


class SignupRedirectMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Veuillez créer un compte ou vous connecter pour accéder aux médecins et spécialités.")
            return redirect("signup")
        return super().dispatch(request, *args, **kwargs)


class DoctorListView(SignupRedirectMixin, ListView):
    model = Medecin
    template_name = "doctors/doctor_list.html"
    context_object_name = "medecins"
    paginate_by = 9

    def get_queryset(self):
        queryset = Medecin.objects.select_related("user", "specialite").filter(is_validated=True)
        specialite = self.request.GET.get("specialite")
        ville = self.request.GET.get("ville")
        nom = self.request.GET.get("nom")

        if specialite:
            queryset = queryset.filter(specialite__nom__icontains=specialite)
        if ville:
            queryset = queryset.filter(ville__icontains=ville)
        if nom:
            queryset = queryset.filter(
                Q(user__first_name__icontains=nom)
                | Q(user__last_name__icontains=nom)
            )
        return queryset.order_by("user__last_name", "user__first_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["specialites"] = Specialite.objects.order_by("nom")
        context["filter_values"] = {
            "specialite": self.request.GET.get("specialite", ""),
            "ville": self.request.GET.get("ville", ""),
            "nom": self.request.GET.get("nom", ""),
        }
        return context


class DoctorDetailView(SignupRedirectMixin, DetailView):
    model = Medecin
    template_name = "doctors/doctor_detail.html"
    context_object_name = "medecin"


class DoctorDashboardView(DoctorRequiredMixin, TemplateView):
    template_name = "doctors/doctor_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medecin = self.request.user.medecin_profile
        today = date.today()
        week_end = today + timedelta(days=7)
        rendez_vous = RendezVous.objects.filter(medecin=medecin)
        weekly = rendez_vous.filter(date__range=(today, week_end))
        stats = Counter(weekly.values_list("statut", flat=True))
        context["medecin"] = medecin
        context["today_appointments"] = rendez_vous.filter(date=today).select_related("patient")
        context["weekly_summary"] = {
            "total": weekly.count(),
            "confirmes": stats.get("confirme", 0),
            "attente": stats.get("en_attente", 0),
            "termines": stats.get("termine", 0),
        }
        context["disponibilites"] = medecin.disponibilites.all()
        context["dates_bloquees"] = medecin.dates_bloquees.order_by("date")[:5]
        return context


class ManageDisponibilitesView(DoctorRequiredMixin, CreateView):
    model = Disponibilite
    form_class = DisponibiliteForm
    template_name = "doctors/manage_dispos.html"
    success_url = reverse_lazy("manage_dispos")

    def form_valid(self, form):
        form.instance.medecin = self.request.user.medecin_profile
        messages.success(self.request, "Disponibilité ajoutée avec succès.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["disponibilites"] = self.request.user.medecin_profile.disponibilites.all()
        return context


class BlockDateView(DoctorRequiredMixin, CreateView):
    model = DateBloquee
    form_class = DateBloqueeForm
    template_name = "doctors/block_date.html"
    success_url = reverse_lazy("block_date")

    def form_valid(self, form):
        form.instance.medecin = self.request.user.medecin_profile
        messages.success(self.request, "Date bloquée enregistrée.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dates_bloquees"] = self.request.user.medecin_profile.dates_bloquees.order_by("date")
        return context
