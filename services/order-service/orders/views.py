import base64
import hashlib
import hmac

from django.conf import settings
from django.db import transaction as db_transaction
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Order, Transaction
from .serializers import OrderSerializer, CreateOrderPayload
from .abacatepay import AbacatePayService
from .catalog_client import CatalogClient
from .finance import FinanceCalculator


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    # Pedidos nunca são editados por PATCH/PUT/DELETE direto — só list/retrieve/create
    # e as transições de estado via as actions dedicadas (deliver/complete/webhook).
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        """
        Filtra os pedidos:
        - Admin vê tudo.
        - Usuário vê apenas o que comprou (client) ou o que vendeu (freelancer).
        """
        user_id = self.request.user.id
        if self.request.user.is_staff:
            return Order.objects.all()

        # Filtra por ID do Cliente OU ID do Freelancer
        return Order.objects.filter(
            Q(client_id=user_id) | Q(freelancer_id=user_id)
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """
        Cria um novo pedido. Gig, pacote, preço e vendedor vêm sempre do
        Catalog Service — nada financeiro é aceito do cliente.
        """
        # 1. Validação dos dados de entrada
        payload = CreateOrderPayload(data=request.data)
        payload.is_valid(raise_exception=True)
        data = payload.validated_data

        try:
            # 2. Validação Externa (Catalog Service) — Gig e Pacote reais
            gig_data = CatalogClient.get_gig_details(data['gig_id'])

            if gig_data.get('status') != 'ATIVO':
                return Response(
                    {"error": "Este Gig não está disponível para venda no momento."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            pacote = CatalogClient.get_pacote(gig_data, data['pacote_id'])

            # 3. Cálculo Financeiro (Split de Taxas) — sempre a partir do preço real do pacote
            finance = FinanceCalculator.calculate_fees(pacote['preco'])

        except ValueError as ve:
            # Captura erros de negócio (ex: valor menor que 80 centavos)
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Captura erros de conexão com Catálogo
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Criação do Pedido (Banco de Dados + Gateway)
        try:
            with db_transaction.atomic():
                # A. Salva o Pedido com os valores calculados
                order = Order.objects.create(
                    client_id=request.user.id,
                    freelancer_id=gig_data['freelancer_id'],
                    gig_id=data['gig_id'],
                    pacote_id=data['pacote_id'],
                    package_title=f"{gig_data.get('titulo', 'Gig')} - {pacote.get('nome', '')}",

                    # Valores Financeiros (Split)
                    amount=finance['amount'],
                    platform_fee=finance['platform_fee'],
                    freelancer_net=finance['freelancer_net'],
                    gateway_fee=finance['gateway_cost'],

                    status='PENDING'
                )

                # B. Chama o Gateway (AbacatePay) — nome/email vêm do usuário autenticado
                customer_data = {
                    'name': request.user.nome_usuario,
                    'email': request.user.email,
                    'cpf': data['customer_cpf']
                }

                abacate = AbacatePayService()
                res = abacate.create_billing(order, customer_data)
                abacate_data = res.get('data', {})

                # C. Registra a Transação
                Transaction.objects.create(
                    order=order,
                    external_id=abacate_data.get('id'),
                    payment_url=abacate_data.get('url'),
                    status='PENDING'
                )

                # Retorna o pedido criado (incluindo o link de pagamento que está no serializer)
                return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Se der erro no Abacate ou no Banco, desfaz tudo (Rollback)
            return Response(
                {"error": "Erro interno ao processar pagamento.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='deliver')
    def deliver_order(self, request, pk=None):
        """
        Ação para o Freelancer entregar o trabalho.
        Muda status de IN_PROGRESS -> DELIVERED.
        """
        order = self.get_object()

        # Apenas o dono do Gig (freelancer) pode entregar
        # Nota: Convertemos para string/int conforme seu model, aqui assumindo comparação segura
        if str(order.freelancer_id) != str(request.user.id):
            return Response({"error": "Acesso negado. Apenas o freelancer responsável pode entregar."}, status=403)

        files = request.data.get('delivery_files')
        note = request.data.get('delivery_note', '')

        if not files:
            return Response({"error": "O link dos arquivos é obrigatório para realizar a entrega."}, status=400)

        with db_transaction.atomic():
            # Lock na linha: evita duas entregas concorrentes (ex: duplo clique) colidirem
            order = Order.objects.select_for_update().get(pk=order.pk)

            if order.status != 'IN_PROGRESS':
                return Response({"error": "O pedido precisa estar pago e em andamento para ser entregue."}, status=400)

            order.delivery_files = files
            order.delivery_note = note
            order.status = 'DELIVERED'
            order.save()

        return Response({"status": "DELIVERED", "message": "Trabalho entregue com sucesso!"})

    @action(detail=True, methods=['post'], url_path='complete')
    def complete_order(self, request, pk=None):
        """
        Ação para o Cliente aceitar e concluir o pedido.
        Muda status de DELIVERED -> COMPLETED.
        Libera o dinheiro (logicamente).
        """
        order = self.get_object()

        # Apenas quem comprou pode finalizar
        if str(order.client_id) != str(request.user.id):
            return Response({"error": "Acesso negado. Apenas o cliente pode finalizar o pedido."}, status=403)

        with db_transaction.atomic():
            # Lock na linha: evita duplo clique/concorrência liberando o pagamento duas vezes
            order = Order.objects.select_for_update().get(pk=order.pk)

            if order.status != 'DELIVERED':
                return Response({"error": "O pedido precisa ter sido entregue pelo freelancer antes de concluir."},
                                status=400)

            order.status = 'COMPLETED'
            order.save()

        # TODO: Chamar microsserviço de Wallet/Withdraw para liberar o saldo 'freelancer_net' para saque.

        return Response({"status": "COMPLETED", "message": "Pedido concluído! O valor foi liberado para o freelancer."})

    def _webhook_secret_valid(self, request):
        expected = settings.ABACATEPAY_WEBHOOK_SECRET
        return bool(expected) and request.query_params.get('webhookSecret') == expected

    def _webhook_signature_valid(self, request):
        signing_key = settings.ABACATEPAY_WEBHOOK_SIGNING_KEY
        signature = request.headers.get('X-Webhook-Signature', '')
        if not signing_key or not signature:
            return False

        expected = base64.b64encode(
            hmac.new(signing_key.encode(), request.body, hashlib.sha256).digest()
        ).decode()
        return hmac.compare_digest(expected, signature)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='webhook')
    def webhook(self, request):
        """
        Recebe notificações da AbacatePay. Autenticidade é garantida por duas
        camadas (documentação oficial: https://docs.abacatepay.com/pages/webhooks):
        o 'webhookSecret' configurado na URL do webhook, e a assinatura
        HMAC-SHA256 no header X-Webhook-Signature sobre o corpo bruto.
        """
        if not self._webhook_secret_valid(request) or not self._webhook_signature_valid(request):
            return Response({"error": "Webhook não autenticado."}, status=status.HTTP_401_UNAUTHORIZED)

        event = request.data.get('event')
        data = request.data.get('data', {})
        bill_id = data.get('id')

        if not bill_id:
            return Response({"received": True})

        try:
            with db_transaction.atomic():
                # Lock na linha pra evitar corrida entre reentregas do mesmo webhook
                tx = Transaction.objects.select_for_update().get(external_id=bill_id)
                order = tx.order

                if event == 'checkout.completed' and tx.status != 'PAID':
                    tx.status = 'PAID'
                    tx.save()
                    if order.status == 'PENDING':
                        order.status = 'IN_PROGRESS'
                        order.save()

                elif event == 'checkout.refunded' and tx.status != 'REFUNDED':
                    tx.status = 'REFUNDED'
                    tx.save()
                    order.status = 'REFUNDED'
                    order.save()

                elif event == 'checkout.disputed' and order.status != 'DISPUTED':
                    order.status = 'DISPUTED'
                    order.save()

        except Transaction.DoesNotExist:
            # Se não achou a transação, ignora (pode ser de outro sistema/ambiente)
            pass

        # Sempre retorna 200 para o Webhook não ficar tentando reenviar
        return Response({"received": True})
