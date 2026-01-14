from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .serializers import TornarSeFreelancerSerializer, PortfolioProjectSerializer, FreelancerSerializer
from .models import Freelancer, PortfolioProject


@extend_schema(tags=['Cadastro de Freelancer'])
class TornarSeFreelancerView(generics.CreateAPIView):
    """
    Endpoint para transformar o usuário logado em Freelancer.

    Requer:
    - Multipart/Form-Data
    - Foto de Perfil
    - Dados Pessoais (Nome, Bio)
    - Arrays de Skills e Idiomas
    - Objeto de Formação
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = TornarSeFreelancerSerializer

    @extend_schema(
        summary="Registrar usuário como Freelancer",
        description="Recebe foto e dados para criar o perfil profissional.",
        responses={201: {"description": "Perfil criado com sucesso", "example": {"detail": "Sucesso", "id": 1}}}
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        freelancer = serializer.save()

        return Response({
            "detail": "Perfil de freelancer criado com sucesso!",
            "id": freelancer.id,
            "nome": freelancer.nome_exibicao
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Portfólio'])
class PortfolioViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de Projetos de Portfólio.
    Permite upload de múltiplos arquivos por projeto.
    """
    serializer_class = PortfolioProjectSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return PortfolioProject.objects.filter(freelancer__id=self.request.user.id).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save()

    @extend_schema(
        summary="Listar projetos",
        description="Retorna apenas os projetos do usuário logado."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Criar novo projeto",
        description="Cria projeto e faz upload dos itens da galeria.",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'titulo': {'type': 'string'},
                    'descricao': {'type': 'string'},
                    'arquivos_upload': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'binary'}
                    }
                }
            }
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)



@extend_schema(tags=['Perfil do Freelancer'])
class FreelancerMeView(generics.RetrieveUpdateAPIView):
    """
    Endpoint para ver e editar o próprio perfil.
    Suporta GET (Ler) e PATCH (Atualizar).
    Para atualizar listas (skills, idiomas), envie a lista completa nova.
    """
    serializer_class = FreelancerSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        # Busca o Freelancer pelo ID do usuário logado
        return generics.get_object_or_404(Freelancer, id=self.request.user.id)

    @extend_schema(
        summary="Obter meu perfil",
        description="Retorna os dados públicos do freelancer logado."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Atualizar meu perfil",
        description="Atualiza campos informados. Para remover uma skill, envie a lista 'skills_input' sem ela.",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'nome': {'type': 'string'},
                    'descricao': {'type': 'string'},
                    'fotoPerfil': {'type': 'string', 'format': 'binary'},
                    'skills_input': {'type': 'array', 'items': {'type': 'string'}},
                    'idiomas_input': {'type': 'array', 'items': {'type': 'string'}},
                    # No Swagger, objetos complexos em multipart são chatos de representar,
                    # mas o backend aceita JSON string ou form-data indexado.
                }
            }
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)