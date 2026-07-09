from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from shared.enums import TipoUsuario, StatusConta, TipoEndereco


class UserManager(BaseUserManager):
    def create_user(self, email, nome_usuario, senha=None, **extra_fields):
        # Correção: Se o serializer enviar 'senha_hash', usamos ela como senha
        if senha is None and 'senha_hash' in extra_fields:
            senha = extra_fields.pop('senha_hash')

        if not email:
            raise ValueError("Email obrigatório")

        email = self.normalize_email(email)
        user = self.model(email=email, nome_usuario=nome_usuario, **extra_fields)

        # set_password faz o hash e salva no campo 'password' do AbstractBaseUser
        user.set_password(senha)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome_usuario, senha=None, **extra_fields):
        extra_fields.setdefault("tipo", TipoUsuario.ADMIN)
        extra_fields.setdefault("status", StatusConta.ATIVO)
        # Flags obrigatórias para superusuário
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, nome_usuario, senha, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    nome_usuario = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)

    # Mantivemos senha_hash para compatibilidade com seu serializer,
    # mas o Django usa internamente o campo 'password' (herdado).
    senha_hash = models.CharField(max_length=255, blank=True)

    tipo = models.CharField(
        max_length=20, choices=TipoUsuario.choices, default=TipoUsuario.CLIENTE
    )
    status = models.CharField(
        max_length=20, choices=StatusConta.choices, default=StatusConta.ATIVO
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    is_social = models.BooleanField(default=False)
    avatar_url = models.URLField(blank=True, null=True)

    # --- Campos Padrão do Django Auth ---
    is_staff = models.BooleanField(default=False)  # Necessário para acessar o Admin
    is_active = models.BooleanField(default=True)  # Necessário para fazer login
    # is_superuser, groups e user_permissions vêm do PermissionsMixin

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome_usuario"]

    def save(self, *args, **kwargs):
        if not self.nome_usuario and self.email:
            self.nome_usuario = self.email.split("@")[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class Pessoa(models.Model):
    id = models.BigAutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nome_completo = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome_completo


class Endereco(models.Model):
    id = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="enderecos"
    )
    tipo = models.CharField(max_length=20, choices=TipoEndereco.choices)
    logradouro = models.CharField(max_length=150)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=100, blank=True)
    cep = models.CharField(max_length=15)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.logradouro}, {self.numero}"