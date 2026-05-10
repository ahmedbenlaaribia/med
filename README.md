# Plateforme de Gestion des Rendez-vous Medicaux

Application Django organisee en architecture MVT avec les apps `base`, `users`, `doctors`, `appointments` et `dashboard`.

## Demarrage rapide

1. Creer un environnement virtuel
```powershell
python -m venv .venv
.venv\Scripts\activate
```

2. Installer les dependances
```powershell
python -m pip install -r requirements.txt
```

3. Lancer les migrations
```powershell
python manage.py makemigrations users doctors appointments
python manage.py migrate
```

4. Creer un superutilisateur
```powershell
python manage.py createsuperuser
```

5. Injecter les medecins de demonstration
```powershell
python manage.py seed_doctors
```

6. Demarrer le serveur
```powershell
python manage.py runserver
```

## Base de donnees

Le projet fonctionne en PostgreSQL par defaut avec la configuration suivante:

```env
DB_ENGINE=postgres
DB_NAME=med-db
DB_USER=postgres
DB_PASSWORD=0000
DB_HOST=localhost
DB_PORT=5432
```

Si vous souhaitez exceptionnellement lancer le projet en SQLite local:

```env
DB_ENGINE=sqlite
```

## Dependances

- Django
- psycopg2-binary
- Pillow
