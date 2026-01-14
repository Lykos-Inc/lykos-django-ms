from celery import shared_task
from django.db import transaction
from .models import Freelancer
import logging

logger = logging.getLogger(__name__)


@shared_task(name='user_created')
def create_profile_for_new_user(user_data):
    """
    Cria um perfil de Freelancer automaticamente quando um usuário é criado no Auth Service.
    user_data espera: {'id': int, 'email': str, 'nome': str, 'tipo': str}
    """
    user_id = user_data.get('id')
    tipo_usuario = user_data.get('tipo')

    logger.info(f"Recebida mensagem para criar perfil: ID {user_id} ({tipo_usuario})")

    # Regra de Negócio: Só criamos perfil para Freelancers?
    # Ou todo mundo tem perfil? No seu diagrama, Cliente e Freelancer são atores distintos,
    # mas o 'Usuario' é comum. Vamos assumir que todos têm um registro base aqui
    # ou filtrar se for apenas FREELANCER.

    # Exemplo: Criar para todos para manter consistência, mas campos ficam vazios
    try:
        if not Freelancer.objects.filter(id=user_id).exists():
            Freelancer.objects.create(
                id=user_id,
                titulo_profissional="Iniciante" if tipo_usuario == 'FREELANCER' else "Cliente"
            )
            logger.info(f"Perfil criado com sucesso para o usuário {user_id}")
        else:
            logger.warning(f"Perfil já existe para usuário {user_id}")

    except Exception as e:
        logger.error(f"Erro ao criar perfil para usuário {user_id}: {str(e)}")
        # Em tarefas reais, poderíamos dar 'raise e' para o Celery tentar de novo (retry)