from django.core.management.base import BaseCommand
from django.core.cache import cache
from profiles.models import Idioma, Habilidade


class Command(BaseCommand):
    help = 'Popula o banco com Idiomas e Habilidades iniciais baseados no Fiverr'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando Seed de Dados...")

        # --- 1. IDIOMAS (Base ISO) ---
        idiomas_data = [
            {'nome': 'Português Brasileiro', 'iso': 'PT_BR'},
            {'nome': 'Português de Portugal', 'iso': 'PT_PT'},
            {'nome': 'Inglês', 'iso': 'EN_US'},
            {'nome': 'Espanhol', 'iso': 'ES_ES'},
            {'nome': 'Francês', 'iso': 'FR_FR'},
            {'nome': 'Alemão', 'iso': 'DE_DE'},
            {'nome': 'Italiano', 'iso': 'IT_IT'},
            {'nome': 'Mandarim', 'iso': 'ZH_CN'},
            {'nome': 'Japonês', 'iso': 'JA_JP'},
            {'nome': 'Russo', 'iso': 'RU_RU'},
        ]

        for item in idiomas_data:
            Idioma.objects.get_or_create(
                iso_codigo=item['iso'],
                defaults={'nome': item['nome']}
            )

        # --- 2. HABILIDADES
        fiverr_skills = [
            # Design e Criativo
            "Design Gráfico", "Design de Logotipo", "Ilustração", "NFT Art",
            "Design de Sites", "UX/UI Design", "Edição de Imagem", "Modelagem 3D",
            "Design de Interiores", "Design de Moda", "Storyboards",

            # Programação e Tech
            "Desenvolvimento Web", "WordPress", "Shopify", "React", "Python",
            "Java", "Mobile Apps", "Desenvolvimento de Games", "DevOps",
            "Cibersegurança", "Data Science", "Machine Learning", "Blockchain",
            "QA e Testes", "Chatbots", "Integração de API",

            # Marketing Digital
            "SEO", "Marketing de Mídia Social", "E-mail Marketing", "SEM",
            "Marketing de Conteúdo", "Marketing de Influência", "E-commerce SEO",
            "Analytics", "Tráfego Pago",

            # Vídeo e Animação
            "Edição de Vídeo", "Animação 2D", "Animação 3D", "Efeitos Visuais",
            "Legendas", "Animação de Logo", "Vídeos Corporativos", "Drones",

            # Escrita e Tradução
            "Redação de Artigos", "Copywriting", "Tradução", "Revisão",
            "Ghostwriting", "Roteiros", "Redação Técnica", "UX Writing",

            # Música e Áudio
            "Produção Musical", "Locução", "Mixagem e Masterização", "Edição de Áudio",
            "Sound Design", "Composição", "Beat Making",

            # Negócios
            "Planos de Negócios", "Assistente Virtual", "Consultoria Jurídica",
            "Gestão de Projetos", "Recursos Humanos", "Pesquisa de Mercado"
        ]

        count_created = 0
        for skill_name in fiverr_skills:
            _, created = Habilidade.objects.get_or_create(nome=skill_name)
            if created:
                count_created += 1

        self.stdout.write(f"Seed concluído: {count_created} novas habilidades inseridas.")

        # --- 3. CACHE ---
        # Cacheia a lista completa para leitura rápida no frontend/backend
        cache.set('lista_idiomas', list(Idioma.objects.values('id', 'nome', 'iso_codigo')), timeout=None)
        cache.set('lista_habilidades', list(Habilidade.objects.values_list('nome', flat=True)), timeout=None)

        self.stdout.write(self.style.SUCCESS('Dados populados e Cache atualizado!'))