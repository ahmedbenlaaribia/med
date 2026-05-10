from django import forms

from .models import RendezVous


class RendezVousForm(forms.ModelForm):
    class Meta:
        model = RendezVous
        fields = ("date", "heure", "motif")
        widgets = {
            "date": forms.HiddenInput(),
            "heure": forms.HiddenInput(),
            "motif": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }
