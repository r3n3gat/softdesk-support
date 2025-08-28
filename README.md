# SoftDesk Support API

API RESTful pour le suivi de bugs et de tâches techniques, bâtie avec **Django** et **Django REST Framework (DRF)**.  
Authentification **JWT**, documentation **Swagger/Redoc**, et suite de tests.

---

## Sommaire

- [Caractéristiques](#caractéristiques)
- [Stack technique](#stack-technique)
- [Prérequis](#prérequis)
- [Installation & Lancement (Poetry)](#installation--lancement-poetry)
- [Configuration (.env)](#configuration-env)
- [Documentation API](#documentation-api)
- [Authentification (JWT)](#authentification-jwt)
- [Ressources & Endpoints](#ressources--endpoints)
- [Permissions (règles métier)](#permissions-règles-métier)
- [Tests & Couverture](#tests--couverture)
- [Structure du projet](#structure-du-projet)
- [CORS (si front séparé)](#cors-si-front-séparé)
- [Checklist production (sécurité & green code)](#checklist-production-sécurité--green-code)
- [Annexes](#annexes)

---

## Caractéristiques

- ✅ CRUD **Projects / Issues / Comments / Contributors**
- ✅ **JWT** (access/refresh) via `djangorestframework-simplejwt`
- ✅ **Permissions** fines (auteur vs contributeur)
- ✅ **Swagger** & **Redoc**
- ✅ Optimisations simples : `select_related` / `prefetch_related`
- ✅ Couverture de tests & rapport **`htmlcov/`**

---

## Stack technique

- Python 3.12+ (3.13 compatible)
- Django 5 + Django REST Framework
- SimpleJWT
- drf-yasg (Swagger)
- python-decouple (configuration par `.env`)
- SQLite par défaut (PostgreSQL possible)

---

## Prérequis

- [Python 3.12+](https://www.python.org/)
- [Poetry](https://python-poetry.org/) installé sur votre machine

---

## Installation & Lancement (Poetry)

Cloner le repo et installer les dépendances :

```bash
git clone <lien-du-repo>
cd softdesk-support
```

## poetry install

Initialiser la base et lancer le serveur : 
```bash
# Fichier .env requis (voir section dédiée)
poetry run python manage.py migrate
poetry run python manage.py runserver

```
Accès local :

API : http://127.0.0.1:8000/

Swagger : http://127.0.0.1:8000/swagger/

Redoc : http://127.0.0.1:8000/redoc/

Astuce : poetry shell ouvre un shell dans l’environnement virtuel.

Configuration (.env)

Créer un fichier .env à la racine :

```bash
# Sécurité
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Base de données (SQLite par défaut)
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=softdesk
# DB_USER=postgres
# DB_PASSWORD=postgres
# DB_HOST=127.0.0.1
# DB_PORT=5432

# Divers
DISABLE_PAGINATION=False
SWAGGER_USE_COMPAT_RENDERERS=False

# Si front séparé (cf. section CORS)
# CORS_ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
# CSRF_TRUSTED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173

```
python-decouple lira automatiquement ce fichier.

## Documentation API

Swagger : http://127.0.0.1:8000/swagger/

Redoc : http://127.0.0.1:8000/redoc/

Pour éviter l’avertissement drf_yasg durant les tests, assurez-vous que votre settings.py contient :
```bash
SWAGGER_USE_COMPAT_RENDERERS = False

```
## Authentification (JWT)

Endpoints (SimpleJWT) :

POST /api/token/ — obtention (credentials : username, password)

POST /api/token/refresh/ — rafraîchissement du refresh token

Header à fournir pour les requêtes authentifiées :
```bash
Authorization: Bearer <access_token>
```
Exemple (cURL) :
```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

```
---
## Ressources & Endpoints

**Projects**

* GET /api/projects/ — liste (pagination désactivée pour coller aux tests)
* POST /api/projects/ — création (alias d’entrée title → name)
* GET /api/projects/{id}/, PATCH /api/projects/{id}/, DELETE /api/projects/{id}/

**Issues**

* GET /api/issues/, POST /api/issues/
* GET /api/issues/{id}/, PATCH /api/issues/{id}/, DELETE /api/issues/{id}/
* Normalisation de status (TODO / IN_PROGRESS / DONE)

**Comments**

* GET /api/comments/ — liste (pagination désactivée pour coller aux tests)
* POST /api/comments/
* GET /api/comments/{id}/, PATCH /api/comments/{id}/, DELETE /api/comments/{id}/

**Contributors**

* GET /api/contributors/
* POST /api/contributors/ — réservé à l’auteur du projet
* DELETE /api/contributors/{id}/ — réservé à l’auteur du projet

Les endpoints exacts proviennent de vos urls.py d’applications (authentication, projects, issues, comments).
La doc Swagger/Redoc reflète automatiquement l’ensemble exposé.

## Permissions (règles métier)

1. [ ] Accès global : authentifié (JWT)
3. [ ] Project : visible par ses contributeurs ; modifiable/supprimable par son auteur
5. [ ] Issue : visible par les contributeurs du projet ; seul l’auteur de l’issue peut modifier/supprimer
7. [ ] Comment : visible par les contributeurs du projet ; seul l’auteur du commentaire peut modifier/supprimer
9. [ ] Gestion des contributors : réservée à l’auteur du projet

## Tests & Couverture

Exécuter la suite de tests :

`poetry run pytest -q`

Générer le rapport de couverture :

`poetry run coverage html`

Ouvrir le rapport :

* Linux/macOS : open htmlcov/index.html
* Windows PowerShell : Start-Process .\htmlcov\index.html

htmlcov/ est le dossier généré par coverage html contenant le rapport HTML de couverture.
À ignorer dans Git (cf. .gitignore).

Recommandé dans pytest.ini (pour taire le warning Swagger) :

```bash
[pytest]
DJANGO_SETTINGS_MODULE = softdesk_support.settings
python_files = tests/test_*.py
filterwarnings =
    ignore:SwaggerJSONRenderer .* SWAGGER_USE_COMPAT_RENDERERS = False:DeprecationWarning
```
## Structure du projet

```bash
softdesk-support/
├── authentication/
├── comments/
├── issues/
├── projects/
├── softdesk_support/    # settings, urls, wsgi
├── tests/
├── manage.py
├── pyproject.toml       # Poetry
├── README.md
└── .env                 # non versionné
```

## Checklist production (sécurité & green code)

1. Sécurité Django

   * DEBUG=False
   * ALLOWED_HOSTS restreint
   * SECURE_SSL_REDIRECT=True
   * SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True
   * SECURE_HSTS_SECONDS=31536000, SECURE_HSTS_INCLUDE_SUBDOMAINS=True, SECURE_HSTS_PRELOAD=True
   
2. JWT

   * Option : rest_framework_simplejwt.token_blacklist + SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"]=True

3. Docs

   * Swagger/Redoc non exposés publiquement (ou protégés)

4. Logs

   * Niveau WARNING/ERROR en prod, pas de logs verbeux

5. Green code

* Garder JSONRenderer en prod (pas de browsable API)
* Laisser la pagination DRF active par défaut (désactivée localement uniquement sur projects et comments pour coller aux tests)
* Utiliser select_related/prefetch_related pour limiter les N+1

## Annexes
Création d’un superuser (optionnel)

`poetry run python manage.py createsuperuser`

Export requirements.txt (compatibilité sans Poetry)

`poetry export -f requirements.txt --output requirements.txt --without-hashes`

Swagger (exemple de configuration urls.py)

Si nécessaire, voici un exemple d’intégration drf-yasg (les routes API sont incluses sous /api/) :
```bash
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="SoftDesk Support API",
        default_version="v1",
        description="API de suivi de bugs/tâches",
        contact=openapi.Contact(email="support@softdesk.local"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("authentication.urls")),
    path("api/", include("projects.urls")),
    path("api/", include("issues.urls")),
    path("api/", include("comments.urls")),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
```
Licence : Projet OpenClassRooms

Contact : ENOTO Stevi, r3n3gat@hotmail.com