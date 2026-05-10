from doctors.models import Specialite


def global_data(request):
    return {
        "nav_specialites": Specialite.objects.order_by("nom")[:7],
    }
