from django.db import models
from django.utils.text import slugify
import uuid


# --- 1. ÁREA (Nível Macro: "Design Gráfico", "Programação") ---
class Area(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


# --- 2. CATEGORIA (Nível Intermediário: "Web Design") ---
class Categoria(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='categorias')
    nome = models.CharField(max_length=100)
    slug = models.SlugField(blank=True)
    icone = models.CharField(max_length=50, blank=True)  # Icone FontAwesome

    class Meta:
        unique_together = ('area', 'slug')  # Evita duplicatas dentro da mesma área

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.area.nome} > {self.nome}"


# --- 3. SUBCATEGORIA (Nível Micro: "Wordpress") ---
class Subcategoria(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategorias')
    nome = models.CharField(max_length=100)
    slug = models.SlugField(blank=True)

    class Meta:
        unique_together = ('categoria', 'slug')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.categoria.nome} > {self.nome}"


def gig_directory_path(instance, filename):
    return f'gigs/user_{instance.freelancer_id}/{instance.slug}/{filename}'


# --- 4. SERVIÇO ---
class Servico(models.Model):
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('PAUSADO', 'Pausado'),
        ('RASCUNHO', 'Rascunho'),
    ]

    freelancer_id = models.BigIntegerField(db_index=True)
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.PROTECT, related_name='servicos')

    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    descricao = models.TextField()
    imagem_capa = models.ImageField(upload_to=gig_directory_path)

    preco_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RASCUNHO')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def categoria(self):
        return self.subcategoria.categoria

    @property
    def area(self):
        return self.subcategoria.categoria.area

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.titulo)
            self.slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo


class Pacote(models.Model):
    TIPO_CHOICES = [('BASICO', 'Básico'), ('PADRAO', 'Padrão'), ('PREMIUM', 'Premium')]
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE, related_name='pacotes')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    prazo_entrega_dias = models.PositiveIntegerField()
    revisoes = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('servico', 'tipo')