from datetime import date
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from celery import current_app

# Importações da SUA lib compartilhada
from shared.utils import validate_cpf, formatar_telefone
from .models import Usuario, Pessoa, Endereco


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nome_usuario', 'email', 'tipo', 'status', 'data_criacao']


class PessoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pessoa
        fields = ['nome_completo', 'cpf', 'data_nascimento', 'telefone']

    def validate_cpf(self, value):
        # Remove pontuação para validar apenas números
        clean_cpf = ''.join(filter(str.isdigit, value))

        try:
            # Usa a função do shared/utils.py
            validate_cpf(clean_cpf)
        except DjangoValidationError as e:
            # Repassa o erro do Django para o DRF com a mensagem correta
            raise serializers.ValidationError(str(e.message))

        # Verifica se já existe (embora o model já tenha unique=True, validação manual ajuda na UX)
        if Pessoa.objects.filter(cpf=clean_cpf).exists():
            raise serializers.ValidationError("Este CPF já está cadastrado.")

        return clean_cpf

    def validate_data_nascimento(self, value):
        # Validação Extra: Idade Mínima
        hoje = date.today()
        idade = hoje.year - value.year - ((hoje.month, hoje.day) < (value.month, value.day))

        if value > hoje:
            raise serializers.ValidationError("A data de nascimento não pode estar no futuro.")
        if idade < 18:
            raise serializers.ValidationError("É necessário ter pelo menos 18 anos para se cadastrar.")

        return value

    def validate_telefone(self, value):
        # Formata o telefone usando a lib shared antes de salvar
        return formatar_telefone(value)


class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = ['tipo', 'logradouro', 'numero', 'complemento', 'cep', 'cidade', 'estado']


class RegisterSerializer(serializers.ModelSerializer):
    pessoa = PessoaSerializer()
    enderecos = EnderecoSerializer(many=True, required=False)
    # Campos de controle (não salvos no banco diretamente)
    senha2 = serializers.CharField(write_only=True, required=True, label="Confirmar Senha")

    class Meta:
        model = Usuario
        fields = ['nome_usuario', 'email', 'senha_hash', 'senha2', 'tipo', 'pessoa', 'enderecos']
        extra_kwargs = {
            'senha_hash': {'write_only': True, 'label': 'Senha'},
            'email': {'error_messages': {'unique': 'Este e-mail já está cadastrado.'}}
        }

    def create(self, validated_data):
        # ... (código existente da transaction.atomic) ...
        with transaction.atomic():
            user = Usuario.objects.create_user(senha=senha, **validated_data)
            Pessoa.objects.create(usuario=user, **pessoa_data)
            for endereco in enderecos_data:
                Endereco.objects.create(usuario=user, **endereco)

        # FORA DO BLOCK ATOMIC (Só envia se salvou no banco com sucesso)
        # Envia mensagem para a fila 'user_created'
        payload = {
            'id': user.id,
            'email': user.email,
            'nome': user.nome_usuario,
            'tipo': user.tipo
        }

        # O queue='celery' é o padrão. O nome da task deve bater com o do profile-service.
        current_app.send_task('user_created', args=[payload])

        return user

    def validate(self, data):
        # Validação de Senha Igual
        if data.get('senha_hash') != data.get('senha2'):
            raise serializers.ValidationError({"senha2": "As senhas não conferem."})
        return data

    def create(self, validated_data):
        pessoa_data = validated_data.pop('pessoa')
        enderecos_data = validated_data.pop('enderecos', [])
        validated_data.pop('senha2')
        senha = validated_data.pop('senha_hash')

        with transaction.atomic():
            # Cria Usuario
            user = Usuario.objects.create_user(senha=senha, **validated_data)

            # Cria Pessoa (os validadores do PessoaSerializer já rodaram antes de chegar aqui)
            Pessoa.objects.create(usuario=user, **pessoa_data)

            # Cria Endereços
            for endereco in enderecos_data:
                Endereco.objects.create(usuario=user, **endereco)

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Claims essenciais para o Traefik
        token['name'] = user.nome_usuario
        token['email'] = user.email
        token['tipo'] = user.tipo
        token['user_id'] = user.id

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'nome_usuario': self.user.nome_usuario,
            'tipo': self.user.tipo
        }
        return data