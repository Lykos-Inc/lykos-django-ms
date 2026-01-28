from rest_framework import serializers
from .models import Area, Categoria, Subcategoria, Servico, Pacote


class SubcategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategoria
        fields = ['id', 'nome', 'slug']


class CategoriaSerializer(serializers.ModelSerializer):
    subcategorias = SubcategoriaSerializer(many=True, read_only=True)

    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'slug', 'icone', 'subcategorias']


class AreaSerializer(serializers.ModelSerializer):
    categorias = CategoriaSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ['id', 'nome', 'slug', 'categorias']


class PacoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pacote
        fields = ['id', 'tipo', 'nome', 'descricao', 'preco', 'prazo_entrega_dias', 'revisoes']


class ServicoDetailSerializer(serializers.ModelSerializer):
    # Exibe a árvore completa na leitura
    area = AreaSerializer(source='subcategoria.categoria.area', read_only=True)
    categoria = CategoriaSerializer(source='subcategoria.categoria', read_only=True)
    subcategoria = SubcategoriaSerializer(read_only=True)

    subcategoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Subcategoria.objects.all(), source='subcategoria', write_only=True
    )
    pacotes = PacoteSerializer(many=True)

    class Meta:
        model = Servico
        fields = [
            'id', 'titulo', 'slug', 'descricao', 'imagem_capa',
            'preco_inicial', 'status', 'freelancer_id',
            'area', 'categoria', 'subcategoria', 'subcategoria_id',
            'pacotes', 'created_at'
        ]

    def create(self, validated_data):
        pacotes_data = validated_data.pop('pacotes')
        servico = Servico.objects.create(**validated_data)
        for pacote in pacotes_data:
            Pacote.objects.create(servico=servico, **pacote)
        return servico


class ServicoListSerializer(serializers.ModelSerializer):
    area_nome = serializers.CharField(source='subcategoria.categoria.area.nome', read_only=True)
    categoria_nome = serializers.CharField(source='subcategoria.categoria.nome', read_only=True)
    subcategoria_nome = serializers.CharField(source='subcategoria.nome', read_only=True)

    class Meta:
        model = Servico
        fields = [
            'id', 'titulo', 'slug', 'imagem_capa',
            'preco_inicial', 'freelancer_id',
            'area_nome', 'categoria_nome', 'subcategoria_nome'
        ]