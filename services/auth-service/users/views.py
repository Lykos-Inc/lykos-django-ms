from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema

from .serializers import (
    UsuarioSerializer, RegisterSerializer, PessoaSerializer,
    EnderecoSerializer, CustomTokenObtainPairSerializer
)
from .models import Usuario, Pessoa, Endereco


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=RegisterSerializer, responses={201: UsuarioSerializer})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UsuarioSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Pega o usuário logado + dados de Pessoa (join otimizado)
        try:
            user = Usuario.objects.select_related('pessoa').get(id=request.user.id)
            user_data = UsuarioSerializer(user).data

            # Adiciona dados da Pessoa se existir
            if hasattr(user, 'pessoa'):
                user_data['pessoa'] = PessoaSerializer(user.pessoa).data

            # Adiciona endereços
            enderecos = user.enderecos.all()
            user_data['enderecos'] = EnderecoSerializer(enderecos, many=True).data

            return Response(user_data)
        except Usuario.DoesNotExist:
            return Response({"detail": "Usuário não encontrado"}, status=404)


# ViewSets mantidos para operações CRUD completas se necessário
class PessoaViewSet(viewsets.ModelViewSet):
    serializer_class = PessoaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Pessoa.objects.filter(usuario=self.request.user)


class EnderecoViewSet(viewsets.ModelViewSet):
    serializer_class = EnderecoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Endereco.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


# --- Endpoint para o Traefik (ForwardAuth) ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_token(request):
    """
    Endpoint leve apenas para o Traefik verificar se o Token é válido.
    Se o middleware 'IsAuthenticated' deixar chegar aqui, é porque é válido.
    """
    # Headers que o Traefik vai injetar na requisição original
    response = Response({"valid": True})
    response["X-User-Id"] = str(request.user.id)
    response["X-User-Email"] = request.user.email
    # Se você tiver um campo 'tipo' (freelancer/cliente), é bom passar também:
    # response["X-User-Type"] = request.user.tipo

    return response