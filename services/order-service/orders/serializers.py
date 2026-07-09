from rest_framework import serializers
from .models import Order, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'external_id', 'payment_url', 'status', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    # Serializa as transações relacionadas (opcional, mas útil para debug)
    transactions = TransactionSerializer(source='transaction_set', many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'client_id',
            'freelancer_id',
            'gig_id',
            'package_title',
            'amount',
            'status',
            'delivery_files',
            'delivery_note',
            'payment_url',  # Link do AbacatePay
            'created_at',
            'updated_at',
            'transactions'
        ]
        # Garante que ninguém consiga editar valores financeiros via API
        read_only_fields = [
            'id',
            'client_id',
            'package_title',
            'platform_fee',
            'freelancer_net',
            'gateway_fee',
            'payment_url',
            'created_at'
        ]


class CreateOrderPayload(serializers.Serializer):
    """
    Valida apenas os dados necessários para INICIAR um pedido.
    O package_title e as taxas são calculados no Backend.
    """
    gig_id = serializers.IntegerField(required=True, help_text="ID do Gig no Catálogo")
    freelancer_id = serializers.IntegerField(required=True, help_text="ID do usuário Freelancer")
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)

    # Dados do Cliente para o AbacatePay (Pix exige CPF)
    customer_name = serializers.CharField(required=True)
    customer_email = serializers.EmailField(required=True)
    customer_cpf = serializers.CharField(required=True, min_length=11, max_length=14)

    def validate(self, data):
        """
        Validações extras se necessário (ex: verificar CPF válido)
        """
        # Exemplo simples: impedir valor negativo
        if data['amount'] <= 0:
            raise serializers.ValidationError("O valor do pedido deve ser positivo.")
        return data