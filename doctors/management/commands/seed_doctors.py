from datetime import time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from doctors.models import Disponibilite, Medecin, Specialite


class Command(BaseCommand):
    help = "Crée les spécialités et 21 médecins de démonstration."

    specialties_data = [
        ("Cardiologie", "cardiologie", "Spécialité du cœur et des vaisseaux."),
        ("Dermatologie", "dermatologie", "Prise en charge des maladies de la peau."),
        ("Pédiatrie", "pediatrie", "Suivi et soins des enfants."),
        ("Ophtalmologie", "ophtalmologie", "Santé des yeux et de la vision."),
        ("Neurologie", "neurologie", "Système nerveux et troubles neurologiques."),
        ("Gynécologie", "gynecologie", "Suivi gynécologique et santé féminine."),
        ("Médecine Générale", "medecine-generale", "Consultations de médecine de premier recours."),
    ]

    doctor_blueprints = {
        "cardiologie": [
            ("Claire", "Martin", "Casablanca", "12 Avenue Hassan II", Decimal("450.00"), "dr.martin.cardio"),
            ("Youssef", "Bennani", "Rabat", "8 Rue des Orangers", Decimal("420.00"), "dr.bennani.cardio"),
            ("Salma", "Idrissi", "Marrakech", "22 Boulevard Atlas", Decimal("470.00"), "dr.idrissi.cardio"),
        ],
        "dermatologie": [
            ("Nadia", "Lahlou", "Casablanca", "15 Rue Taddart", Decimal("350.00"), "dr.lahlou.derma"),
            ("Karim", "El Fassi", "Fès", "4 Avenue Mohammed V", Decimal("380.00"), "dr.elfassi.derma"),
            ("Ines", "Alaoui", "Agadir", "19 Rue des Dunes", Decimal("360.00"), "dr.alaoui.derma"),
        ],
        "pediatrie": [
            ("Samir", "Othmani", "Rabat", "31 Rue Al Kindi", Decimal("300.00"), "dr.othmani.pedia"),
            ("Meryem", "Chraibi", "Tanger", "10 Avenue Mohammed VI", Decimal("320.00"), "dr.chraibi.pedia"),
            ("Adil", "Naciri", "Meknès", "5 Rue Al Amal", Decimal("310.00"), "dr.naciri.pedia"),
        ],
        "ophtalmologie": [
            ("Hicham", "Berrada", "Casablanca", "28 Rue Ibn Sina", Decimal("500.00"), "dr.berrada.ophta"),
            ("Sara", "Mokri", "Rabat", "6 Avenue Annakhil", Decimal("520.00"), "dr.mokri.ophta"),
            ("Omar", "Jabri", "Oujda", "14 Boulevard Zerktouni", Decimal("490.00"), "dr.jabri.ophta"),
        ],
        "neurologie": [
            ("Leila", "Kadiri", "Casablanca", "11 Rue Ghandi", Decimal("560.00"), "dr.kadiri.neuro"),
            ("Rachid", "Tazi", "Fès", "2 Rue Saiss", Decimal("540.00"), "dr.tazi.neuro"),
            ("Amal", "Hassani", "Marrakech", "45 Quartier Hivernage", Decimal("580.00"), "dr.hassani.neuro"),
        ],
        "gynecologie": [
            ("Khadija", "Benkirane", "Rabat", "17 Avenue Fal Ould Oumeir", Decimal("400.00"), "dr.benkirane.gyne"),
            ("Nour", "Ait Said", "Agadir", "9 Rue Souss", Decimal("390.00"), "dr.aitsaid.gyne"),
            ("Yasmine", "Zerouali", "Casablanca", "7 Boulevard Anfa", Decimal("430.00"), "dr.zerouali.gyne"),
        ],
        "medecine-generale": [
            ("Mehdi", "Bousfiha", "Casablanca", "3 Rue des Lilas", Decimal("220.00"), "dr.bousfiha.general"),
            ("Amina", "Sabri", "Rabat", "26 Avenue des FAR", Decimal("240.00"), "dr.sabri.general"),
            ("Zakaria", "Mouline", "Tanger", "18 Rue de la Corniche", Decimal("230.00"), "dr.mouline.general"),
        ],
    }

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        password = "Doctor@1234"
        created_rows = []

        specialties = {}
        for name, slug, description in self.specialties_data:
            specialite, _ = Specialite.objects.get_or_create(
                slug=slug,
                defaults={"nom": name, "description": description},
            )
            specialties[slug] = specialite

        for slug, doctors in self.doctor_blueprints.items():
            specialite = specialties[slug]
            for index, (first_name, last_name, ville, adresse, tarif, username) in enumerate(doctors, start=1):
                email = f"{username}@medrdv.local"
                user, user_created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "is_doctor": True,
                        "is_patient": False,
                    },
                )
                if user_created:
                    user.set_password(password)
                    user.save()

                medecin, _ = Medecin.objects.get_or_create(
                    user=user,
                    defaults={
                        "specialite": specialite,
                        "adresse": adresse,
                        "ville": ville,
                        "tarif": tarif,
                        "description": f"Dr. {first_name} {last_name} exerce en {specialite.nom.lower()} avec une approche centrée sur le patient.",
                        "is_validated": True,
                    },
                )

                if not medecin.disponibilites.exists():
                    Disponibilite.objects.create(
                        medecin=medecin,
                        jour="lun",
                        heure_debut=time(9, 0),
                        heure_fin=time(17, 0),
                    )
                    Disponibilite.objects.create(
                        medecin=medecin,
                        jour="mer",
                        heure_debut=time(9, 0),
                        heure_fin=time(13, 0),
                    )

                created_rows.append((username, password, specialite.nom, ville))

        header = f"{'Nom d utilisateur':<24} {'Mot de passe':<16} {'Specialite':<22} {'Ville':<15}"
        separator = "-" * len(header)
        self.stdout.write(self.style.SUCCESS("Médecins de démonstration disponibles :"))
        self.stdout.write(header)
        self.stdout.write(separator)
        for username, pwd, specialite, ville in created_rows:
            self.stdout.write(f"{username:<24} {pwd:<16} {specialite:<22} {ville:<15}")
