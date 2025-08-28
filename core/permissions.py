from rest_framework import permissions
from projects.models import Contributor, Project

def _get_project_from_obj(obj):
    if isinstance(obj, Project):
        return obj
    if hasattr(obj, "project"):
        return obj.project
    if hasattr(obj, "issue") and hasattr(obj.issue, "project"):
        return obj.issue.project
    return None

def _is_contributor(user, project: Project) -> bool:
    if not user or not user.is_authenticated or not project:
        return False
    return Contributor.objects.filter(project=project, user=user).exists()

class IsAuthorOrReadOnlyWithinProject(permissions.BasePermission):
    """
    Lecture: réservée aux contributeurs du projet.
    Écriture: réservée à l'auteur de l'objet (Issue/Comment).
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        project = _get_project_from_obj(obj)
        if request.method in permissions.SAFE_METHODS:
            return _is_contributor(request.user, project)
        return getattr(obj, "author_id", None) == getattr(request.user, "id", None)

class IsProjectAuthorOrReadOnly(permissions.BasePermission):
    """
    Lecture: réservée aux contributeurs du projet.
    Écriture: réservée à l'auteur du projet (pour Project).
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        project = _get_project_from_obj(obj)
        if request.method in permissions.SAFE_METHODS:
            return _is_contributor(request.user, project or obj)
        target = project or obj
        return getattr(target, "author_id", None) == getattr(request.user, "id", None)

class IsSelf(permissions.BasePermission):
    """Lecture/écriture autorisées uniquement sur soi-même (ProfileView)."""
    def has_object_permission(self, request, view, obj):
        return obj == request.user
