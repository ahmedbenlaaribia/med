from django import forms

from .models import DateBloquee, Disponibilite, Medecin


class MedecinProfileForm(forms.ModelForm):
    class Meta:
        model = Medecin
        fields = ("adresse", "ville", "tarif", "description", "photo")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css_class = "form-control"
            if name == "photo":
                field.widget.attrs.update({"class": "form-control"})
            else:
                field.widget.attrs.update({"class": css_class})


class DisponibiliteForm(forms.ModelForm):
    class Meta:
        model = Disponibilite
        fields = ("jour", "heure_debut", "heure_fin")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class DateBloqueeForm(forms.ModelForm):
    class Meta:
        model = DateBloquee
        fields = ("date", "motif")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "motif": forms.TextInput(attrs={"class": "form-control"}),
        }
