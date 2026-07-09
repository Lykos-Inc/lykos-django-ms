from django.db import models
import uuid


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('PAID', 'Pago'),
        ('IN_PROGRESS', 'Em Andamento'),
        ('DELIVERED', 'Entregue'),
        ('COMPLETED', 'Concluído'),
        ('CANCELLED', 'Cancelado'),
        ('REFUNDED', 'Reembolsado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # --- Dados de Referência ---
    client_id = models.IntegerField(help_text="ID do usuário (Auth Service) que comprou")
    freelancer_id = models.IntegerField(help_text="ID do usuário (Auth Service) que vendeu")
    gig_id = models.IntegerField(help_text="ID do Gig (Catalog Service)")
    package_title = models.CharField(max_length=200, help_text="Snapshot do título na hora da compra")

    # --- Financeiro (Split de Pagamento) ---
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Valor TOTAL pago pelo cliente")

    platform_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Valor bruto retido pela Lykos (Ex: 10%)"
    )

    freelancer_net = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Valor líquido que vai para o saldo do freelancer"
    )

    gateway_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Custo do AbacatePay (R$ 0.80), pago de dentro da taxa da Lykos"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    # --- Entrega do Serviço ---
    delivery_files = models.URLField(max_length=500, blank=True, null=True,
                                     help_text="Link para arquivos (MinIO/Drive)")
    delivery_note = models.TextField(blank=True, null=True, help_text="Mensagem de entrega do freelancer")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{str(self.id)[:8]} - {self.status} (R$ {self.amount})"


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('PAID', 'Pago'),
        ('FAILED', 'Falhou'),
        ('REFUNDED', 'Reembolsado'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')

    # AbacatePay Data
    external_id = models.CharField(max_length=100, unique=True, help_text="ID da cobrança no AbacatePay (bill_...)")
    payment_url = models.URLField(max_length=500, help_text="URL para o cliente pagar")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=50, default='PIX')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transação {self.external_id} - {self.status}"