from django.db import models

class StatusConta(models.TextChoices):
    ATIVO = "ATIVO", "Ativo"
    SUSPENSO = "SUSPENSO", "Suspenso"
    BANIDO = "BANIDO", "Banido"
    INATIVO = "INATIVO", "Inativo"

class StatusPerfil(models.TextChoices):
    ATIVO = "ATIVO", "Ativo"
    DESATIVADO = "DESATIVADO", "Desativado"
    BANIDO = "BANIDO", "Banido"
    SUSPENSO = "SUSPENSO", "Suspenso"

class NivelIdioma(models.TextChoices):
    BASICO = "BASICO", "Básico"
    INTERMEDIARIO = "INTERMEDIARIO", "Intermediário"
    AVANCADO = "AVANCADO", "Avançado"
    NATIVO = "NATIVO", "Nativo"

class StatusPacote(models.TextChoices):
    ATIVO = "ATIVO", "Ativo"
    INATIVO = "INATIVO", "Inativo"
    PAUSADO = "PAUSADO", "Pausado"

class StatusPagamento(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    PAGO = "PAGO", "Pago"
    CANCELADO = "CANCELADO", "Cancelado"
    ESTORNADO = "ESTORNADO", "Estornado"

class StatusAgendamento(models.TextChoices):
    AGENDADO = "AGENDADO", "Agendado"
    CONCLUIDO = "CONCLUIDO", "Concluído"
    CANCELADO = "CANCELADO", "Cancelado"

class StatusRelatorio(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    ACEITA = "ACEITA", "Aceita"
    REJEITADA = "REJEITADA", "Rejeitada"

class TipoEndereco(models.TextChoices):
    RESIDENCIAL = "RESIDENCIAL", "Residencial"
    COMERCIAL = "COMERCIAL", "Comercial"
    OUTRO = "OUTRO", "Outro"

class TipoMidia(models.TextChoices):
    IMAGEM = "IMAGEM", "Imagem"
    VIDEO = "VIDEO", "Vídeo"
    DOCUMENTO = "DOCUMENTO", "Documento"