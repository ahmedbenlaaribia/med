from django.db import models

from users.models import CustomUser


class Specialite(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=120, unique=True)

    def __str__(self):
        return self.nom


class Medecin(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="medecin_profile",
    )
    specialite = models.ForeignKey(
        Specialite,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medecins",
    )
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    tarif = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to="doctors/", null=True, blank=True)
    is_validated = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"


class Disponibilite(models.Model):
    JOURS = [
        ("lun", "Lundi"),
        ("mar", "Mardi"),
        ("mer", "Mercredi"),
        ("jeu", "Jeudi"),
        ("ven", "Vendredi"),
        ("sam", "Samedi"),
    ]

    medecin = models.ForeignKey(
        Medecin,
        on_delete=models.CASCADE,
        related_name="disponibilites",
    )
    jour = models.CharField(max_length=3, choices=JOURS)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

    def __str__(self):
        return f"{self.medecin} - {self.get_jour_display()}"


class DateBloquee(models.Model):
    medecin = models.ForeignKey(
        Medecin,
        on_delete=models.CASCADE,
        related_name="dates_bloquees",
    )
    date = models.DateField()
    motif = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ("medecin", "date")

    def __str__(self):
        return f"{self.medecin} - {self.date}"
