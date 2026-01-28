import os
import requests
import uuid


class AbacatePayService:
    def __init__(self):
        self.api_key = os.environ.get('ABACATEPAY_API_KEY', '')
        self.base_url = "https://api.abacatepay.com/v1"  # URL Base da API (Exemplo)

    def create_billing(self, order, customer_data):
        """
        Cria uma cobrança Pix no AbacatePay.
        Recebe: Objeto Order e Dicionário customer_data
        Retorna: Dict com 'id' e 'url' da cobrança
        """

        # Se não tiver chave de API configurada, retornamos um MOCK (Simulação)
        # Isso permite que você teste o fluxo sem quebrar se não tiver conta lá ainda.
        if not self.api_key or self.api_key == "dummy_key":
            return self._mock_response(order)

        # --- Lógica Real (Descomente quando tiver a API Key) ---
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "amount": int(order.amount * 100), # Valor em centavos
            "customer": customer_data,
            "metadata": {"order_id": str(order.id)}
        }
        response = requests.post(f"{self.base_url}/billing/create", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

        # Por segurança, retornamos o Mock enquanto não configuramos a API real
        return self._mock_response(order)

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