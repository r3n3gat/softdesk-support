from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from authentication.views import SignupView, ProfileView

# Swagger / Redoc
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="SoftDesk Support API",
        default_version="v1",
        description="API de suivi de bugs et de tâches techniques (Django + DRF, JWT, permissions, docs).",
        contact=openapi.Contact(email="<r3n3gat@hotmail.com>"),

    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Auth/JWT — expose les deux conventions pour convenir à tous les clients
    path("api/login/", TokenObtainPairView.as_view(), name="token_obtain_pair_alias"),
    path("api/refresh/", TokenRefreshView.as_view(), name="token_refresh_alias"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Signup / profil
    path("api/signup/", SignupView.as_view(), name="signup"),
    path("api/me/", ProfileView.as_view(), name="profile"),

    # Apps
    path("api/projects/", include("projects.urls")),
    path("api/issues/", include("issues.urls")),
    path("api/comments/", include("comments.urls")),

    # Docs
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
