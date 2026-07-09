from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# CORREÇÃO: Importar de 'catalog' em vez de 'core'
from catalog.views import AreaViewSet, CategoriaViewSet, SubcategoriaViewSet, ServicoViewSet

router = DefaultRouter()
router.register(r'areas', AreaViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'subcategorias', SubcategoriaViewSet)
router.register(r'servicos', ServicoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/catalog/', include(router.urls)), # Prefixo api/catalog já está no router do Traefik, mas manter aqui é boa prática

    # Swagger
    path('api/catalog/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/catalog/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]