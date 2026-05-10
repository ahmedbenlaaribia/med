from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class PatientRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_patient:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)


class DoctorRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_doctor:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)
