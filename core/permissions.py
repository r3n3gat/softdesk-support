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
    return Contributor.objects.filter(project=project, user=user).exists()

class IsObjectAuthorOrReadOnly(permissions.BasePermission):
    """Lecture pour tous les contributeurs, écriture réservée à l’auteur."""
    def has_object_permission(self, request, view, obj):
        project = _get_project_from_obj(obj)
        if request.method in permissions.SAFE_METHODS:
            return _is_contributor(request.user, project)
        return getattr(obj, "author_id", None) == getattr(request.user, "id", None)

class IsProjectAuthor(permissions.BasePermission):
    """L’auteur du projet a tous les droits sur ce projet et ses ressources."""
    def has_object_permission(self, request, view, obj):
        project = _get_project_from_obj(obj)
        return project and project.author_id == getattr(request.user, "id", None)

class IsProjectMemberOrReadOnly(permissions.BasePermission):
    """Contributeur requis pour lire. Modification : auteur du projet uniquement."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        project = _get_project_from_obj(obj)
        if request.method in permissions.SAFE_METHODS:
            return _is_contributor(request.user, project)
        return project and project.author_id == getattr(request.user, "id", None)

class IsSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user
