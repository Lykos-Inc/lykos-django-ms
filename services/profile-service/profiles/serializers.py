import json
from rest_framework import serializers
from django.db import transaction
from .models import Freelancer, Formacao, Habilidade, Idioma, FreelancerIdioma, PortfolioProject, PortfolioItem
from shared.enums import NivelIdioma


# --- Serializers Auxiliares ---

class FormacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formacao
        fields = ['titulo', 'instituicao', 'ano_conclusao']


# --- Cadastro Inicial (Tornar-se Freelancer) ---

class TornarSeFreelancerSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='nome_exibicao')
    descricao = serializers.CharField(source='bio')
    fotoPerfil = serializers.ImageField(source='foto_perfil', required=True)
    skills = serializers.ListField(child=serializers.CharField(), write_only=True)
    idiomas = serializers.ListField(child=serializers.CharField(), write_only=True)
    formacao = serializers.JSONField(write_only=True, required=True)

    class Meta:
        model = Freelancer
        fields = ['nome', 'descricao', 'fotoPerfil', 'skills', 'idiomas', 'formacao']

    def create(self, validated_data):
        skills_names = validated_data.pop('skills', [])
        idiomas_names = validated_data.pop('idiomas', [])
        formacao_data = validated_data.pop('formacao', {})

        user_id = self.context['request'].user.id

        with transaction.atomic():
            freelancer, created = Freelancer.objects.update_or_create(
                id=user_id,
                defaults={
                    'nome_exibicao': validated_data.get('nome_exibicao'),
                    'bio': validated_data.get('bio'),
                    'foto_perfil': validated_data.get('foto_perfil')
                }
            )

            if skills_names:
                freelancer.habilidades.clear()
                for name in skills_names:
                    skill_obj, _ = Habilidade.objects.get_or_create(nome=name)
                    freelancer.habilidades.add(skill_obj)

            if idiomas_names:
                FreelancerIdioma.objects.filter(freelancer=freelancer).delete()
                for idioma_nome in idiomas_names:
                    try:
                        idioma_obj = Idioma.objects.get(nome__iexact=idioma_nome)
                        FreelancerIdioma.objects.create(
                            freelancer=freelancer,
                            idioma=idioma_obj,
                            nivel=NivelIdioma.FLUENTE
                        )
                    except Idioma.DoesNotExist:
                        pass

            if formacao_data:
                freelancer.formacoes.all().delete()
                Formacao.objects.create(
                    freelancer=freelancer,
                    titulo=formacao_data.get('titulo'),
                    instituicao=formacao_data.get('instituicao'),
                    ano_conclusao=formacao_data.get('ano')
                )

        return freelancer


# --- Portfólio ---

class PortfolioItemSerializer(serializers.ModelSerializer):
    url = serializers.FileField(source='arquivo', read_only=True)

    class Meta:
        model = PortfolioItem
        fields = ['id', 'url', 'tipo_midia']


class PortfolioProjectSerializer(serializers.ModelSerializer):
    items = PortfolioItemSerializer(many=True, read_only=True)
    arquivos_upload = serializers.ListField(
        child=serializers.FileField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = PortfolioProject
        fields = ['id', 'titulo', 'descricao', 'url_externa', 'items', 'arquivos_upload', 'created_at']
        read_only_fields = ['freelancer']

    def create(self, validated_data):
        arquivos = validated_data.pop('arquivos_upload', [])
        user_id = self.context['request'].user.id
        freelancer = Freelancer.objects.get(id=user_id)

        project = PortfolioProject.objects.create(freelancer=freelancer, **validated_data)

        for i, arquivo in enumerate(arquivos):
            PortfolioItem.objects.create(
                project=project,
                arquivo=arquivo,
                ordem=i,
                tipo_midia='VIDEO' if arquivo.content_type.startswith('video') else 'IMAGEM'
            )

        return project


# --- Edição e Visualização de Perfil (/me) ---

class FreelancerSerializer(serializers.ModelSerializer):
    skills = serializers.SlugRelatedField(
        many=True,
        slug_field='nome',
        queryset=Habilidade.objects.all(),
        source='habilidades'
    )
    idiomas = serializers.SerializerMethodField()
    formacoes = FormacaoSerializer(many=True, required=False)

    fotoPerfil = serializers.ImageField(source='foto_perfil', required=False)
    nome = serializers.CharField(source='nome_exibicao', required=False)
    descricao = serializers.CharField(source='bio', required=False)

    skills_input = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    idiomas_input = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    formacoes_input = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )

    class Meta:
        model = Freelancer
        fields = [
            'id', 'nome', 'descricao', 'fotoPerfil',
            'skills', 'skills_input',
            'idiomas', 'idiomas_input',
            'formacoes', 'formacoes_input'
        ]
        read_only_fields = ['id']

    def get_idiomas(self, obj):
        return [fi.idioma.nome for fi in obj.idiomas.all()]

    def update(self, instance, validated_data):
        instance.nome_exibicao = validated_data.get('nome_exibicao', instance.nome_exibicao)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.foto_perfil = validated_data.get('foto_perfil', instance.foto_perfil)
        instance.save()

        if 'skills_input' in validated_data:
            skills_names = validated_data['skills_input']
            new_skills = []
            for name in skills_names:
                skill_obj, _ = Habilidade.objects.get_or_create(nome=name)
                new_skills.append(skill_obj)
            instance.habilidades.set(new_skills)

        if 'idiomas_input' in validated_data:
            idiomas_names = validated_data['idiomas_input']
            FreelancerIdioma.objects.filter(freelancer=instance).delete()
            for name in idiomas_names:
                try:
                    idioma_obj = Idioma.objects.get(nome__iexact=name)
                    FreelancerIdioma.objects.create(
                        freelancer=instance,
                        idioma=idioma_obj,
                        nivel=NivelIdioma.FLUENTE
                    )
                except Idioma.DoesNotExist:
                    pass

        if 'formacoes_input' in validated_data:
            formacoes_data = validated_data['formacoes_input']
            instance.formacoes.all().delete()
            for form_data in formacoes_data:
                Formacao.objects.create(
                    freelancer=instance,
                    titulo=form_data.get('titulo'),
                    instituicao=form_data.get('instituicao'),
                    ano_conclusao=form_data.get('ano_conclusao') or form_data.get('ano')
                )

        return instance