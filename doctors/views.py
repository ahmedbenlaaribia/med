from collections import Counter
from datetime import date, timedelta

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from appointments.models import RendezVous
from users.mixins import DoctorRequiredMixin

from .forms import DateBloqueeForm, DisponibiliteForm
from .models import DateBloquee, Disponibilite, Medecin, Specialite


def get_role_dashboard_url(user):
    if user.is_staff or user.is_superuser:
        return "admin_dashboard"
    if user.is_doctor:
        return "doctor_dashboard"
    return "home"


class SignupRedirectMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Veuillez creer un compte ou vous connecter pour acceder aux medecins et specialites.")
            return redirect("signup")
        return super().dispatch(request, *args, **kwargs)


class DoctorsPublicAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_patient:
            messages.info(request, "Cet espace est reserve aux patients.")
            return redirect(get_role_dashboard_url(request.user))
        return super().dispatch(request, *args, **kwargs)


class DoctorListView(DoctorsPublicAccessMixin, SignupRedirectMixin, ListView):
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


class DoctorDetailView(DoctorsPublicAccessMixin, SignupRedirectMixin, DetailView):
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
        context["disponibilites"] = medecin.disponibilites.order_by("jour", "heure_debut")
        context["dates_bloquees"] = medecin.dates_bloquees.order_by("date")[:5]
        return context


class DoctorScheduleContextMixin:
    template_name = "doctors/manage_dispos.html"

    def get_medecin(self):
        return self.request.user.medecin_profile

    def get_schedule_context(
        self,
        *,
        dispo_form=None,
        blocked_date_form=None,
        edit_dispo=None,
        edit_dispo_form=None,
        edit_blocked_date=None,
        edit_blocked_date_form=None,
    ):
        medecin = self.get_medecin()
        if edit_dispo is None:
            edit_dispo_id = self.request.GET.get("edit_dispo")
            if edit_dispo_id:
                edit_dispo = get_object_or_404(Disponibilite, pk=edit_dispo_id, medecin=medecin)
        if edit_blocked_date is None:
            edit_blocked_date_id = self.request.GET.get("edit_blocked_date")
            if edit_blocked_date_id:
                edit_blocked_date = get_object_or_404(DateBloquee, pk=edit_blocked_date_id, medecin=medecin)

        if dispo_form is None:
            dispo_form = DisponibiliteForm(prefix="dispo")
        if blocked_date_form is None:
            blocked_date_form = DateBloqueeForm(prefix="block")
        if edit_dispo and edit_dispo_form is None:
            edit_dispo_form = DisponibiliteForm(instance=edit_dispo, prefix=f"edit-dispo-{edit_dispo.pk}")
        if edit_blocked_date and edit_blocked_date_form is None:
            edit_blocked_date_form = DateBloqueeForm(
                instance=edit_blocked_date,
                prefix=f"edit-block-{edit_blocked_date.pk}",
            )

        return {
            "medecin": medecin,
            "dispo_form": dispo_form,
            "blocked_date_form": blocked_date_form,
            "disponibilites": medecin.disponibilites.order_by("jour", "heure_debut"),
            "dates_bloquees": medecin.dates_bloquees.order_by("date"),
            "edit_dispo": edit_dispo,
            "edit_dispo_form": edit_dispo_form,
            "edit_blocked_date": edit_blocked_date,
            "edit_blocked_date_form": edit_blocked_date_form,
            "schedule_stats": {
                "weekly_slots": medecin.disponibilites.count(),
                "blocked_dates": medecin.dates_bloquees.count(),
                "upcoming_appointments": RendezVous.objects.filter(
                    medecin=medecin,
                    date__gte=date.today(),
                    statut__in=["en_attente", "confirme"],
                ).count(),
            },
        }

    def render_schedule(self, **kwargs):
        return render(self.request, self.template_name, self.get_schedule_context(**kwargs))


class ManageDisponibilitesView(DoctorRequiredMixin, DoctorScheduleContextMixin, TemplateView):
    template_name = "doctors/manage_dispos.html"

    def get_context_data(self, **kwargs):
        return self.get_schedule_context()


class CreateDisponibiliteView(DoctorRequiredMixin, DoctorScheduleContextMixin, View):
    def post(self, request, *args, **kwargs):
        form = DisponibiliteForm(request.POST, prefix="dispo")
        if form.is_valid():
            disponibilite = form.save(commit=False)
            disponibilite.medecin = self.get_medecin()
            disponibilite.save()
            messages.success(request, "Le creneau a ete ajoute.")
            return redirect("manage_dispos")
        return self.render_schedule(dispo_form=form)


class UpdateDisponibiliteView(DoctorRequiredMixin, DoctorScheduleContextMixin, View):
    def post(self, request, *args, **kwargs):
        disponibilite = get_object_or_404(
            Disponibilite,
            pk=kwargs["pk"],
            medecin=self.get_medecin(),
        )
        form = DisponibiliteForm(
            request.POST,
            instance=disponibilite,
            prefix=f"edit-dispo-{disponibilite.pk}",
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Le creneau a ete modifie.")
            return redirect("manage_dispos")
        return self.render_schedule(edit_dispo=disponibilite, edit_dispo_form=form)

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(["POST"])


class CreateBlockedDateView(DoctorRequiredMixin, DoctorScheduleContextMixin, View):
    def post(self, request, *args, **kwargs):
        form = DateBloqueeForm(request.POST, prefix="block")
        if form.is_valid():
            medecin = self.get_medecin()
            selected_date = form.cleaned_data["date"]
            if DateBloquee.objects.filter(medecin=medecin, date=selected_date).exists():
                form.add_error("date", "Cette date est deja bloquee.")
                return self.render_schedule(blocked_date_form=form)
            blocked_date = form.save(commit=False)
            blocked_date.medecin = medecin
            blocked_date.save()
            messages.success(request, "La date bloquee a ete ajoutee.")
            return redirect("manage_dispos")
        return self.render_schedule(blocked_date_form=form)


class UpdateBlockedDateView(DoctorRequiredMixin, DoctorScheduleContextMixin, View):
    def post(self, request, *args, **kwargs):
        blocked_date = get_object_or_404(
            DateBloquee,
            pk=kwargs["pk"],
            medecin=self.get_medecin(),
        )
        form = DateBloqueeForm(
            request.POST,
            instance=blocked_date,
            prefix=f"edit-block-{blocked_date.pk}",
        )
        if form.is_valid():
            selected_date = form.cleaned_data["date"]
            if DateBloquee.objects.filter(
                medecin=self.get_medecin(),
                date=selected_date,
            ).exclude(pk=blocked_date.pk).exists():
                form.add_error("date", "Cette date est deja bloquee.")
                return self.render_schedule(edit_blocked_date=blocked_date, edit_blocked_date_form=form)
            form.save()
            messages.success(request, "La date bloquee a ete modifiee.")
            return redirect("manage_dispos")
        return self.render_schedule(edit_blocked_date=blocked_date, edit_blocked_date_form=form)

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(["POST"])


class DeleteDisponibiliteView(DoctorRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        disponibilite = get_object_or_404(
            Disponibilite,
            pk=kwargs["pk"],
            medecin=request.user.medecin_profile,
        )
        disponibilite.delete()
        messages.success(request, "Le creneau a ete supprime.")
        return redirect("manage_dispos")

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(["POST"])


class DeleteBlockedDateView(DoctorRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        blocked_date = get_object_or_404(
            DateBloquee,
            pk=kwargs["pk"],
            medecin=request.user.medecin_profile,
        )
        blocked_date.delete()
        messages.success(request, "La date bloquee a ete supprimee.")
        return redirect("manage_dispos")

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(["POST"])


class BlockDateView(DoctorRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return redirect("manage_dispos")

    def post(self, request, *args, **kwargs):
        return redirect("manage_dispos")
