from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSellerAndOwnerOrReadOnly(BasePermission):
    """
    Leitura é pública (o catálogo é vitrine). Escrita exige um vendedor
    autenticado; alterar ou remover um Servico já existente exige também
    ser o dono dele (freelancer_id == user.id).
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, 'is_seller', False))

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return str(obj.freelancer_id) == str(request.user.id)
