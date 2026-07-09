import os
import uuid
from decimal import ROUND_HALF_UP

import requests


class AbacatePayService:
    def __init__(self):
        self.api_key = os.environ.get('ABACATEPAY_API_KEY', '')
        self.base_url = "https://api.abacatepay.com/v1"
        self.return_url = os.environ.get('ABACATEPAY_RETURN_URL', 'https://lykos.example.com/checkout')
        self.completion_url = os.environ.get('ABACATEPAY_COMPLETION_URL', 'https://lykos.example.com/checkout/sucesso')

    def create_billing(self, order, customer_data):
        """
        Cria uma cobrança Pix (checkout) no AbacatePay.
        Recebe: Objeto Order e Dicionário customer_data ({name, email, cpf})
        Retorna: Dict no formato {"data": {"id":..., "url":...}, "error": None}
        Referência: https://docs.abacatepay.com/api-reference/criar-uma-nova-cobranca
        """

        # Se não tiver chave de API configurada, retornamos um MOCK (Simulação)
        # Isso permite que você teste o fluxo sem quebrar se não tiver conta lá ainda.
        if not self.api_key or self.api_key == "dummy_key":
            return self._mock_response(order)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        price_cents = int((order.amount * 100).to_integral_value(rounding=ROUND_HALF_UP))
        payload = {
            "frequency": "ONE_TIME",
            "methods": ["PIX"],
            "products": [{
                "externalId": str(order.id),
                "name": order.package_title,
                "quantity": 1,
                "price": price_cents,
            }],
            "returnUrl": self.return_url,
            "completionUrl": self.completion_url,
            "customer": {
                "name": customer_data['name'],
                "email": customer_data['email'],
                "taxId": customer_data['cpf'],
            },
            "externalId": str(order.id),
        }
        response = requests.post(f"{self.base_url}/billing/create", json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def _mock_response(self, order):
        """Simula uma resposta positiva da API"""
        fake_id = f"bill_{uuid.uuid4().hex[:10]}"
        return {
            "data": {
                "id": fake_id,
                "url": f"https://abacatepay.com/pay/{fake_id}",  # URL Fictícia
                "status": "PENDING"
            }
        }
