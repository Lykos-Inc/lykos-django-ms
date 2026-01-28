from django.urls import path, include
from rest_framework.routers import DefaultRouter
from dj_rest_auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordChangeView,
    LogoutView
)
from .views import (
    RegisterView,
    LoginView,
    MeView,
    PessoaViewSet,
    EnderecoViewSet,
    validate_token
)

router = DefaultRouter()
router.register(r'pessoas', PessoaViewSet, basename='pessoas')
router.register(r'enderecos', EnderecoViewSet, basename='enderecos')

urlpatterns = [
    # --- Rotas Customizadas (Nossas) ---
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),  # Seu login com JWT Customizado
    path('me/', MeView.as_view(), name='me'),

    # Logout (opcional, pois JWT é stateless, mas útil para blacklist se configurado)
    path('logout/', LogoutView.as_view(), name='rest_logout'),

    # Reset de Senha (Envia E-mail)
    path('password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),

    # Confirmação do Reset (Link do E-mail)
    path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Troca de senha (usuário logado)
    path('password/change/', PasswordChangeView.as_view(), name='rest_password_change'),

    # --- Rotas do Router (CRUDs) ---
    path('', include(router.urls)),
    # Rota usada pelo Traefik
    path('api/auth/validate/', validate_token, name='token_validate'),
]