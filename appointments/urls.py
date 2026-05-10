from django.urls import path

from .views import (
    BookAppointmentView,
    CancelAppointmentView,
    DoctorAppointmentsView,
    PatientAppointmentsView,
    UpdateAppointmentStatusView,
)

urlpatterns = [
    path("reserver/<int:medecin_id>/", BookAppointmentView.as_view(), name="book_appointment"),
    path("mes-rdv/", PatientAppointmentsView.as_view(), name="patient_appointments"),
    path("annuler/<int:pk>/", CancelAppointmentView.as_view(), name="cancel_appointment"),
    path("medecin/rdv/", DoctorAppointmentsView.as_view(), name="doctor_appointments"),
    path("medecin/rdv/<int:pk>/statut/", UpdateAppointmentStatusView.as_view(), name="update_statut"),
]
