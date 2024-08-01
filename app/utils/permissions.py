from rest_framework import permissions


class HasAPIkey(permissions.BasePermission):
    message = "VALID API KEY REQUIRED"

    def has_permission(self, request, view):
        return (
            request.headers.get("api_key") == "6ca72ea05f741259253e8f80db186aa043c43b51" or
            request.headers.get("apiKey") == "6ca72ea05f741259253e8f80db186aa043c43b51"
        )


class HasAPIKeyAndIsAuthenticated(permissions.IsAuthenticated):
    message = "VALID API KEY REQUIRED"

    def has_permission(self, request, view):
        return super().has_permission(request, view) and HasAPIkey().has_permission(request, view)
