from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import CustomUserCreationForm, ProfileUpdateForm
from .models import CustomUser


class SignupView(SuccessMessageMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "users/signup.html"
    success_url = reverse_lazy("login")
    success_message = "Votre compte patient a été créé avec succès. Vous pouvez maintenant vous connecter."


class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs.update({"class": "form-control"})
        return form

    def get_success_url(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return reverse("admin_dashboard")
        if user.is_doctor:
            return reverse("doctor_dashboard")
        if user.is_patient:
            return reverse("patient_appointments")
        return reverse("home")


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("home")


class ProfileView(UpdateView):
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Votre profil a été mis à jour.")
        return super().form_valid(form)
