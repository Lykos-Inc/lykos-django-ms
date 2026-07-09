from celery import shared_task
from .models import Freelancer
import logging

logger = logging.getLogger(__name__)


@shared_task(name='user_created')
def create_profile_for_new_user(user_data):
    """
    Todo usuário nasce comprador; comprador não tem perfil de vendedor aqui.
    O perfil de Freelancer só é criado quando o auth-service dispara 'seller_activated'.
    """
    logger.info(f"Usuário criado: ID {user_data.get('id')} (comprador)")


@shared_task(name='seller_activated')
def create_freelancer_profile(user_data):
    """
    Cria o esqueleto do perfil de Freelancer quando o usuário ativa o modo
    vendedor no auth-service (POST /api/auth/become-seller/).
    user_data espera: {'id': int, 'email': str, 'nome': str}
    """
    user_id = user_data.get('id')

    try:
        _, created = Freelancer.objects.get_or_create(
            id=user_id,
            defaults={'nome_exibicao': user_data.get('nome') or 'Novo Freelancer'}
        )
        if created:
            logger.info(f"Perfil de freelancer criado para o usuário {user_id}")
        else:
            logger.warning(f"Perfil de freelancer já existia para o usuário {user_id}")
    except Exception as e:
        logger.error(f"Erro ao criar perfil de freelancer para {user_id}: {str(e)}")
