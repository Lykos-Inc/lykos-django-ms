import os
from celery import Celery

# Define o settings padrão do Django para o Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_service.settings')

app = Celery('auth_service')

# Lê as configurações do settings.py que começam com CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre tarefas (tasks.py) em todos os apps instalados automaticamente
app.autodiscover_tasks()