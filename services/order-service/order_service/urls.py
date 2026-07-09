from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from orders.views import OrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/orders/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/orders/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # --- API (ROUTER) ---
    path('api/', include(router.urls)),
]