from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Area, Categoria, Subcategoria, Servico
from .serializers import (
    AreaSerializer,
    CategoriaSerializer,
    SubcategoriaSerializer,
    ServicoDetailSerializer,
    ServicoListSerializer
)


class AreaViewSet(viewsets.ReadOnlyModelViewSet):
    """Lista as grandes áreas (Ex: Design, Programação)"""
    queryset = Area.objects.all().prefetch_related('categorias')
    serializer_class = AreaSerializer
    pagination_class = None


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    pagination_class = None


class SubcategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subcategoria.objects.all()
    serializer_class = SubcategoriaSerializer
    pagination_class = None


class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.all().select_related(
        'subcategoria__categoria__area'
    ).prefetch_related('pacotes')

    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Filtros atualizados para a nova estrutura
    filterset_fields = ['subcategoria', 'subcategoria__categoria', 'freelancer_id', 'status']
    search_fields = ['titulo', 'descricao']
    ordering_fields = ['preco_inicial', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ServicoListSerializer
        return ServicoDetailSerializer

    def perform_create(self, serializer):
        serializer.save(freelancer_id=self.request.user.id)