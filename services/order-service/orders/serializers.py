from rest_framework import serializers
from .models import Order, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'external_id', 'payment_url', 'status', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    # Serializa as transações relacionadas (opcional, mas útil para debug)
    transactions = TransactionSerializer(many=True, read_only=True)
    payment_url = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'client_id',
            'freelancer_id',
            'gig_id',
            'pacote_id',
            'package_title',
            'amount',
            'status',
            'delivery_files',
            'delivery_note',
            'payment_url',  # Link do AbacatePay (da transação mais recente)
            'created_at',
            'updated_at',
            'transactions'
        ]
        # Pedidos só mudam de estado via as actions dedicadas (create/deliver/complete/webhook),
        # nunca por PATCH/PUT direto — ver OrderViewSet.http_method_names.
        read_only_fields = [
            'id',
            'client_id',
            'freelancer_id',
            'gig_id',
            'pacote_id',
            'package_title',
            'amount',
            'status',
            'platform_fee',
            'freelancer_net',
            'gateway_fee',
            'payment_url',
            'created_at'
        ]

    def get_payment_url(self, obj):
        tx = obj.transactions.order_by('-created_at').first()
        return tx.payment_url if tx else None


class CreateOrderPayload(serializers.Serializer):
    """
    Valida apenas os dados necessários para INICIAR um pedido.
    freelancer_id, amount e package_title nunca vêm do cliente: são derivados
    do Gig/Pacote reais no Catalog Service e dos claims do usuário autenticado.
    """
    gig_id = serializers.IntegerField(required=True, help_text="ID do Gig no Catálogo")
    pacote_id = serializers.IntegerField(required=True, help_text="ID do Pacote escolhido")

    # Pix exige CPF do pagador; não existe em nenhum outro lugar hoje, então
    # continua sendo informado no checkout.
    customer_cpf = serializers.CharField(required=True, min_length=11, max_length=14)
