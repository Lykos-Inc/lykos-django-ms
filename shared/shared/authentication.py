from rest_framework_simplejwt.authentication import JWTAuthentication


class RemoteUser:
    """Usuário reconstruído a partir dos claims do JWT emitido pelo auth-service.

    Os demais serviços não têm a tabela Usuario (ela só existe no auth-service),
    então não há o que consultar em banco local: os claims já são a fonte de verdade.
    """
    is_authenticated = True
    is_anonymous = False

    def __init__(self, token):
        self.id = self.pk = token.get('user_id')
        self.email = token.get('email')
        self.nome_usuario = token.get('name')
        self.is_buyer = token.get('is_buyer', False)
        self.is_seller = token.get('is_seller', False)
        self.is_staff = token.get('is_staff', False)

    def __str__(self):
        return self.email or str(self.id)


class RemoteJWTAuthentication(JWTAuthentication):
    """Valida o JWT assinado pelo auth-service sem consultar um banco local."""

    def get_user(self, validated_token):
        return RemoteUser(validated_token)
