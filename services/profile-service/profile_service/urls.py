from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/profiles/', include('profiles.urls')),

    # Documentação Swagger
    path('api/profiles/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/profiles/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
]