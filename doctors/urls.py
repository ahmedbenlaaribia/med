from django.urls import path

from .views import (
    BlockDateView,
    CreateBlockedDateView,
    CreateDisponibiliteView,
    DeleteBlockedDateView,
    DeleteDisponibiliteView,
    DoctorDashboardView,
    DoctorDetailView,
    DoctorListView,
    ManageDisponibilitesView,
    UpdateBlockedDateView,
    UpdateDisponibiliteView,
)

urlpatterns = [
    path("", DoctorListView.as_view(), name="doctor_list"),
    path("dashboard/", DoctorDashboardView.as_view(), name="doctor_dashboard"),
    path("disponibilites/", ManageDisponibilitesView.as_view(), name="manage_dispos"),
    path("disponibilites/ajouter/", CreateDisponibiliteView.as_view(), name="create_dispo"),
    path("disponibilites/<int:pk>/modifier/", UpdateDisponibiliteView.as_view(), name="update_dispo"),
    path("disponibilites/<int:pk>/supprimer/", DeleteDisponibiliteView.as_view(), name="delete_dispo"),
    path("bloquer-date/", BlockDateView.as_view(), name="block_date"),
    path("bloquer-date/ajouter/", CreateBlockedDateView.as_view(), name="create_blocked_date"),
    path("bloquer-date/<int:pk>/modifier/", UpdateBlockedDateView.as_view(), name="update_blocked_date"),
    path("bloquer-date/<int:pk>/supprimer/", DeleteBlockedDateView.as_view(), name="delete_blocked_date"),
    path("<int:pk>/", DoctorDetailView.as_view(), name="doctor_detail"),
]
