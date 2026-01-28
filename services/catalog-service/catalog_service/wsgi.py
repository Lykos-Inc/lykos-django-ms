import os
from django.core.wsgi import get_wsgi_application

# Define o arquivo de settings padrão
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'catalog_service.settings')

# Cria a aplicação WSGI
application = get_wsgi_application()