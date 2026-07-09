from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Area, Categoria, Subcategoria, Servico
from .permissions import IsSellerAndOwnerOrReadOnly
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

    permission_classes = [IsSellerAndOwnerOrReadOnly]
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

    @action(detail=False, methods=['get'], url_path=r'by-id/(?P<gig_id>\d+)')
    def by_id(self, request, gig_id=None):
        """
        Lookup interno por ID numérico, usado por outros serviços (ex: order-service)
        que referenciam o Gig pelo id, já que a rota pública usa slug.
        """
        servico = get_object_or_404(self.get_queryset(), pk=gig_id)
        return Response(ServicoDetailSerializer(servico).data)