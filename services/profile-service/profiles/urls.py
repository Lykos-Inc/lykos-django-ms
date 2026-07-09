from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TornarSeFreelancerView, PortfolioViewSet, FreelancerMeView # <--- Importe aqui

router = DefaultRouter()
router.register(r'portfolio', PortfolioViewSet, basename='portfolio')

urlpatterns = [
    path('become-freelancer/', TornarSeFreelancerView.as_view(), name='become-freelancer'),
    path('me/', FreelancerMeView.as_view(), name='freelancer-me'), # <--- Nova rota
    path('', include(router.urls)),
]