from django.core.management.base import BaseCommand
from catalog.models import Area, Categoria, Subcategoria


class Command(BaseCommand):
    help = 'Popula o banco com Áreas, Categorias e Subcategorias'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando Seed Completo...")

        # Estrutura baseada no arquivo fornecido
        dados = {
            "Design Gráfico": {
                "Logotipo e Identidade de Marca": ["Design de Logo", "Manual de Identidade de Marca",
                                                   "Cartões de Visita e Papelaria", "Tipografia e Fontes",
                                                   "Direção de Arte"],
                "Design de Aplicativos e Web": ["Design de Sites", "Design de Aplicativos", "UX Design",
                                                "Design de Landing Page", "Design de Ícones"],
                "Arte e Ilustração": ["Ilustração", "Artistas de IA", "Design de avatar com IA",
                                      "Ilustração e Desenho de Livro Infantil", "Ilustração em Quadrinhos",
                                      "Ilustração de Desenho Animado", "Retratos e Caricaturas Digitais",
                                      "Design de Estampas", "Design de Tatuagens", "Storyboards", "Arte NFT"],
                "Design Visual": ["Edição de Imagem", "Edição de Imagem com IA", "Design de PowerPoint",
                                  "Design de Infográficos", "Vetorização de Logos e Imagens", "Design de Currículos"],
                "Design de Impressão": ["Design de Flyers", "Design de Panfletos", "Design de Pôster",
                                        "Design de Catálogos", "Design de Menus", "Design de Convites"],
                "Embalagem e Capas": ["Design de Embalagens e Rótulos", "Layout de Livros", "Capas de Livros",
                                      "Design de Capa de CD", "Capas para Podcasts", "Criação de Car Wraps"],
                "Design 3D": ["Arquitetura 3D", "Desenho Industrial 3D", "Moda e Vestuário 3D", "Paisagem 3D",
                              "Design de joias 3D"],
                "Design de Marketing": ["Design para Mídia Social", "Design de Miniaturas", "Design de E-mail",
                                        "Banner Digital", "Design de Sinalização"],
                "Moda e Mercadorias": ["Camisetas e Mercadorias", "Design de Moda", "Design de Joias"]
            },
            "Programação e Tecnologia": {
                "Sites": ["Desenvolvimento de Sites", "Manutenção de Site", "WordPress", "Shopify",
                          "Sites Personalizados"],
                "Desenvolvimento de Aplicativos": ["Apps Web Full Stack", "Aplicativos de Desktop",
                                                   "Desenvolvimento de Games", "Desenvolvimento de Chatbot",
                                                   "Extensões de Navegador"],
                "Desenvolvimento de Software": ["Desenvolvimento de Software", "Desenvolvimento de IA",
                                                "APIs e Integrações", "Redação de roteiro"],
                "Mobile Apps": ["Desenvolvimento de Aplicativo Mobile", "Aplicativos Multiplataforma",
                                "Desenvolvimento de Aplicativos Android", "Desenvolvimento de Aplicativos iOS",
                                "Manutenção de Aplicativo Móvel"],
                "Plataformas de Sites": ["Wix", "Webflow", "GoDaddy", "Squarespace", "WooCommerce"],
                "Suporte e Cybersecurity": ["Suporte de TI", "Computação em nuvem", "Engenharia de DevOps",
                                            "Segurança Cibernética", "Conversão de Arquivos"],
                "Blockchain e Criptomoeda": ["Desenvolvimento e soluções de blockchain",
                                             "Aplicativos Descentralizados (dApps)", "Design da Moeda e Tokenização",
                                             "Auditoria e Segurança de Blockchain", "Plataformas de Câmbio"]
            },
            "Marketing Digital": {
                "Pesquisar": ["Otimização para Mecanismos de Pesquisa (SEO)",
                              "Marketing para Mecanismos de Busca (SEM)", "SEO Local", "SEO para E-commerce",
                              "SEO de Vídeo"],
                "Social": ["Marketing de Mídias Sociais", "Mídia Social Paga", "Comércio social",
                           "Marketing de Influência", "Comunidades Online"],
                "Métodos e Técnicas": ["Vídeo Marketing", "Marketing para E-commerce", "E-mail Marketing",
                                       "Automação de E-mail", "Automação de marketing", "Marketing de Afiliados",
                                       "Relações Públicas", "Crowdfunding", "SMS Marketing"],
                "Analytics e Estratégia": ["Estratégia de Marketing", "Estratégia de Marca",
                                           "Estratégia de marketing digital", "Conceitos de Marketing e Ideação",
                                           "Web Analytics", "Assessoria em Marketing"]
            },
            "Vídeo e Animação": {
                "Edição e Pós-Produção": ["Edição de Vídeo", "Efeitos Visuais", "Arte para vídeos",
                                          "Vídeos de Intro e Outro", "Legendas e Closed Caption"],
                "Vídeos de MKT e Mídia Social": ["Comerciais e Anúncios em Vídeo", "Vídeos para Mídia Social",
                                                 "Vídeos de Música", "Vídeos de Slides"],
                "Vídeos Explicativos": ["Vídeos Explicativos Animados", "Vídeos Explicativos em Live Action",
                                        "Vídeos de Screencasting", "Produção de Vídeo de E-learning"],
                "Animação": ["Animação de Personagem", "GIFs Animados", "Animações Infantis", "Animação para Streamers",
                             "Animação NFT"],
                "Vídeos de Produtos": ["Animação 3D de Produtos", "Vídeos de Produtos para E-commerce",
                                       "Vídeos Corporativos", "Pré-visualizações de App e Sites"],
                "Design de Animação": ["Animação de Logo", "Animação Web e Lottie", "Animação de texto"]
            },
            "Redação e Tradução": {
                "Redação de Conteúdo": ["Artigos e posts para blog", "Estratégia de conteúdo", "Conteúdo para Sites",
                                        "Redação de Roteiros", "Escrita Criativa", "Redação para Podcast",
                                        "Redação para Discursos", "Pesquisa e Resumos"],
                "Edição e Crítica": ["Revisão e Edição", "Apoio acadêmico", "Edição de Conteúdo de IA",
                                     "Assessoria em Redação"],
                "Publicação de Livros": ["Redação de Livros e E-books", "Edição de Livros", "Leitura Beta"],
                "Tradução e Transcrição": ["Traduções", "Localização", "Transcrição", "Interpretação"],
                "Redação de Negócios": ["Voz e Tom de Marca", "Nomes Comerciais e Slogans", "Estudos de Caso",
                                        "Descrição de Produtos", "Redação Promocional", "Redação de E-mails",
                                        "Copywriting para mídias sociais", "Press Releases", "UX Writing"],
                "Redação sobre Carreira": ["Criação de Currículos", "Cartas de Apresentação", "Perfis do LinkedIn",
                                           "Descrições de Trabalho"]
            },
            "Música e Áudio": {
                "Produção Musical e Letras": ["Produtores musicais", "Compositores", "Beat Making",
                                              "Cantores e Vocalistas", "Músicos de Sessão", "Jingles e Intros"],
                "Engenharia de Áudio": ["Mixagem e Masterização", "Edição de Áudio", "Afinação de Voz",
                                        "Logotipo Sonoro"],
                "Locução e Streaming": ["Locução", "Produção de Podcast", "Produção de Audiolivros",
                                        "Produção de Anúncios de Áudio", "Síntese de Voz e IA"],
                "Aulas e Transcrição": ["Aulas de Música Online", "Transcrição Musical",
                                        "Assessoria em Música e Áudio"],
                "Serviços de DJ": ["Remixes", "Vinhetas e Drops para DJ", "Mixagem DJ"],
                "Design de Som": ["Design de Som", "Efeitos Sonoros", "Música de Meditação"]
            },
            "Negócios": {
                "Formação e Consultoria": ["Formação e Registro Comercial", "Pesquisa de Mercado", "Planos de Negócio",
                                           "Consultoria de Negócios", "Consultoria de RH", "Consultoria de IA"],
                "Operações e Gerenciamento": ["Assistente Virtual", "Gerenciamento de Projeto",
                                              "Gerenciamento de E-commerce", "Gerenciamento de Supply Chain",
                                              "Gestão de produtos"],
                "Serviços Legais": ["Gestão de Propriedade Intelectual", "Documentos legais e contratos",
                                    "Assessoria Jurídica Geral"],
                "Vendas e Atendimento": ["Vendas", "Geração de Leads", "Atendimento ao Cliente"],
                "Diversos": ["Apresentações", "Investigações Online", "Consultoria de Sustentabilidade"]
            },
            "Finanças": {
                "Serviços de Contabilidade": ["Relatórios Financeiros", "Contabilidade",
                                              "Gestão de Folha de Pagamento"],
                "Consultoria Tributária": ["Declarações Tributárias", "Planejamento Tributário",
                                           "Conformidade Tributária"],
                "Finanças Corporativas": ["Due Diligence", "Avaliação", "Consultoria para Fusões e Aquisições"],
                "Planejamento Financeiro": ["Orçamento e Previsão", "Modelagem Financeira", "Análise de Custos",
                                            "Análise de Ações"],
                "Gestão Patrimonial": ["Gestão de Orçamento Pessoal", "Consultoria de Investimentos",
                                       "Aulas de Trading Online", "Coaching Financeiro"]
            },
            "Dados": {
                "Ciência de Dados e ML": ["Machine Learning", "Visão Computacional", "PLN", "Deep Learning",
                                          "Modelos Generativos"],
                "Coleta de Dados": ["Data Entry", "Raspagem de dados", "Digitação de Dados", "Limpeza de Dados"],
                "Análise de Dados": ["Visualização de Dados", "Data Analytics", "Painéis de Controle"],
                "Gerenciamento de Dados": ["Engenharia de Dados", "Banco de Dados", "Governança e Proteção de Dados"]
            },
            "Fotografia": {
                "Produto": ["Fotógrafos de Produtos", "Fotógrafos de Alimentos"],
                "Pessoas": ["Fotógrafos de Retratos", "Fotógrafos de Eventos", "Fotógrafos de Lifestyle e Moda"],
                "Cenas": ["Fotógrafos Imobiliários", "Fotógrafos Paisagísticos", "Fotógrafos com Drones"],
                "Diversos": ["Criação de Presets de Fotos", "Conselhos fotográficos"]
            }
        }

        total_areas = 0
        total_cats = 0
        total_subs = 0

        for area_nome, categorias in dados.items():
            area_obj, created_area = Area.objects.get_or_create(nome=area_nome)
            if created_area: total_areas += 1

            for cat_nome, subcategorias in categorias.items():
                cat_obj, created_cat = Categoria.objects.get_or_create(
                    area=area_obj,
                    nome=cat_nome,
                    defaults={'icone': 'fa-folder'}  # Ícone genérico por enquanto
                )
                if created_cat: total_cats += 1

                for sub_nome in subcategorias:
                    _, created_sub = Subcategoria.objects.get_or_create(
                        categoria=cat_obj,
                        nome=sub_nome
                    )
                    if created_sub: total_subs += 1

        self.stdout.write(self.style.SUCCESS(
            f'Sucesso! {total_areas} Áreas, {total_cats} Categorias e {total_subs} Subcategorias criadas.'))