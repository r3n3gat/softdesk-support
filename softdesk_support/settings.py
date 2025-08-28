from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from authentication.views import SignupView, ProfileView

# Swagger / Redoc
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(title="SoftDesk API", default_version="v1"),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth/JWT
    path("api/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
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
