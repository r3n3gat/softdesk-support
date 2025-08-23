# SoftDesk Support API

API RESTful pour le suivi de bugs et tâches techniques, construite avec Django & Django REST Framework.

## 🔧 Installation locale

```bash
git clone <lien-du-repo>
cd softdesk-support
poetry install  # ou pipenv install
poetry shell    # ou pipenv shell
python manage.py migrate
python manage.py runserver
```

🧪 Tests
```bash
python manage.py test
```

🔐 Authentification
```bash
JWT via djangorestframework-simplejwt

```

Endpoints :

api/token/ : login (username, password)

api/token/refresh/ : refresh du token

---

📚 Documentation API : 

Documentation générée avec Swagger via drf-yasg

/swagger/ : Documentation interactive

/redoc/ : Documentation ReDoc

---
🛡️ Sécurité 

RGPD : gestion de l’âge, consentement et droit à l’oubli

OWASP : permissions fines, tokens JWT, contrôle d’accès

Green Code : pagination intégrée
---
🧩 Ressources principales : 
User, Project, Contributor, Issue, Comment
---
📁 Structure du projet : 
```bash
softdesk_support/
├── authentication/
├── projects/
├── issues/
├── comments/
└── softdesk_support/
```
---

## 🚀 Swagger setup (à ajouter dans `softdesk_support/urls.py`)

```python
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="SoftDesk Support API",
        default_version='v1',
        description="API de suivi de bugs/tâches",
        contact=openapi.Contact(email="support@softdesk.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('authentication.urls')),
    path('api/', include('projects.urls')),
    path('api/', include('issues.urls')),
    path('api/', include('comments.urls')),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]