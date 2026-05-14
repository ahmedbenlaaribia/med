from collections import defaultdict
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, FormView, TemplateView

from doctors.models import DateBloquee, Medecin
from users.mixins import DoctorRequiredMixin, PatientRequiredMixin

from .forms import RendezVousForm
from .models import RendezVous


def get_available_slots(medecin, num_days=14):
    slots = []
    today = date.today()
    booked = set(
        RendezVous.objects.filter(medecin=medecin)
        .exclude(statut="annule")
        .values_list("date", "heure")
    )
    blocked = set(
        DateBloquee.objects.filter(medecin=medecin)
        .values_list("date", flat=True)
    )
    day_map = {
        "lun": 0,
        "mar": 1,
        "mer": 2,
        "jeu": 3,
        "ven": 4,
        "sam": 5,
    }

    for i in range(num_days):
        current_date = today + timedelta(days=i)
        if current_date in blocked:
            continue
        weekday = current_date.weekday()
        for dispo in medecin.disponibilites.all():
            if day_map.get(dispo.jour) == weekday:
                current = datetime.combine(current_date, dispo.heure_debut)
                end = datetime.combine(current_date, dispo.heure_fin)
                while current < end:
                    current_time = current.time().replace(second=0, microsecond=0)
                    if (current_date, current_time) not in booked:
                        slots.append((current_date, current_time))
                    current += timedelta(minutes=30)
    return slots


class DoctorBookingRestrictedMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_patient:
            if request.user.is_staff or request.user.is_superuser:
                messages.info(request, "L'administration n'accede pas a la reservation des rendez-vous.")
                return redirect("admin_dashboard")
            if request.user.is_doctor:
                messages.info(request, "Un medecin ne peut pas prendre de rendez-vous sur la plateforme.")
                return redirect("doctor_dashboard")
        return super().dispatch(request, *args, **kwargs)


class BookAppointmentView(DoctorBookingRestrictedMixin, PatientRequiredMixin, FormView):
    template_name = "appointments/book.html"
    form_class = RendezVousForm

    def dispatch(self, request, *args, **kwargs):
        self.medecin = get_object_or_404(Medecin, pk=kwargs["medecin_id"], is_validated=True)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["date"].required = False
        form.fields["heure"].required = False
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slots = get_available_slots(self.medecin)
        grouped_slots = defaultdict(list)
        for slot_date, slot_time in slots:
            grouped_slots[slot_date].append(slot_time)
        context["medecin"] = self.medecin
        context["grouped_slots"] = dict(grouped_slots)
        return context

    def form_valid(self, form):
        selected_slot = self.request.POST.get("slot")
        if not selected_slot:
            messages.error(self.request, "Veuillez sélectionner un créneau disponible.")
            return self.form_invalid(form)

        try:
            date_str, time_str = selected_slot.split("|", 1)
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            selected_time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            messages.error(self.request, "Le créneau sélectionné est invalide.")
            return self.form_invalid(form)

        available_slots = set(get_available_slots(self.medecin))
        if (selected_date, selected_time) not in available_slots:
            messages.error(self.request, "Ce créneau n'est plus disponible.")
            return self.form_invalid(form)

        RendezVous.objects.create(
            patient=self.request.user,
            medecin=self.medecin,
            date=selected_date,
            heure=selected_time,
            motif=form.cleaned_data.get("motif", ""),
            statut="en_attente",
        )
        messages.success(self.request, "Votre rendez-vous a été réservé avec succès.")
        return redirect("patient_appointments")


class PatientAppointmentsView(PatientRequiredMixin, TemplateView):
    template_name = "appointments/patient_appointments.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        appointments = (
            RendezVous.objects.select_related("medecin__user", "medecin__specialite")
            .filter(patient=self.request.user)
        )
        upcoming = []
        history = []
        for appointment in appointments:
            if appointment.date >= today and appointment.statut != "annule":
                upcoming.append(appointment)
            else:
                history.append(appointment)
        context["upcoming_appointments"] = upcoming
        context["history_appointments"] = history
        return context


class CancelAppointmentView(PatientRequiredMixin, DetailView):
    model = RendezVous
    template_name = "appointments/cancel_confirm.html"
    context_object_name = "appointment"

    def get_queryset(self):
        return RendezVous.objects.filter(patient=self.request.user).select_related("medecin__user")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.statut not in {"en_attente", "confirme"}:
            messages.error(request, "Ce rendez-vous ne peut pas être annulé.")
            return redirect("patient_appointments")
        self.object.statut = "annule"
        self.object.save(update_fields=["statut"])
        messages.success(request, "Le rendez-vous a été annulé.")
        return redirect("patient_appointments")


class DoctorAppointmentsView(DoctorRequiredMixin, TemplateView):
    template_name = "appointments/doctor_appointments.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medecin = self.request.user.medecin_profile
        selected_date = self.request.GET.get("date")
        appointments = RendezVous.objects.select_related("patient").filter(medecin=medecin)
        if selected_date:
            appointments = appointments.filter(date=selected_date)
        context["appointments"] = appointments
        context["selected_date"] = selected_date or ""
        return context


class UpdateAppointmentStatusView(DoctorRequiredMixin, View):
    allowed_statuses = {"confirme", "annule", "termine"}

    def post(self, request, *args, **kwargs):
        appointment = get_object_or_404(
            RendezVous,
            pk=kwargs["pk"],
            medecin=request.user.medecin_profile,
        )
        new_status = request.POST.get("statut")
        if new_status not in self.allowed_statuses:
            messages.error(request, "Statut invalide.")
            return redirect("doctor_appointments")
        if appointment.statut != "en_attente":
            messages.info(request, "Une action a deja ete appliquee a ce rendez-vous.")
            return redirect("doctor_appointments")
        appointment.statut = new_status
        appointment.save(update_fields=["statut"])
        messages.success(request, "Le statut du rendez-vous a été mis à jour.")
        return redirect("doctor_appointments")

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(["POST"])
