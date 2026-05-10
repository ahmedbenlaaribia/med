from django.urls import path

from .views import (
    BlockDateView,
    DoctorDashboardView,
    DoctorDetailView,
    DoctorListView,
    ManageDisponibilitesView,
)

urlpatterns = [
    path("", DoctorListView.as_view(), name="doctor_list"),
    path("dashboard/", DoctorDashboardView.as_view(), name="doctor_dashboard"),
    path("disponibilites/", ManageDisponibilitesView.as_view(), name="manage_dispos"),
    path("bloquer-date/", BlockDateView.as_view(), name="block_date"),
    path("<int:pk>/", DoctorDetailView.as_view(), name="doctor_detail"),
]
