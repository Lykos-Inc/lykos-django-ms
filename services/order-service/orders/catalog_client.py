import requests
from rest_framework.exceptions import ValidationError


class CatalogClient:
    # URL interna do Docker (nome do serviço no docker-compose)
    BASE_URL = "http://catalog-service:8000/api/catalog"

    @classmethod
    def get_gig_details(cls, gig_id):
        """
        Consulta o Catalog Service para pegar detalhes do Gig.
        """
        try:
            url = f"{cls.BASE_URL}/gigs/{gig_id}/"
            response = requests.get(url, timeout=5)

            if response.status_code == 404:
                raise ValidationError(f"Gig {gig_id} não encontrado no catálogo.")

            if response.status_code != 200:
                raise ValidationError("Erro de comunicação com o serviço de catálogo.")

            return response.json()

        except requests.exceptions.RequestException:
            # Se o Catalog Service estiver offline
            raise ValidationError("Serviço de Catálogo indisponível no momento.")

    @classmethod
    def validate_price(cls, gig_data, amount):
        """
        Valida se o valor pago bate com o valor do Gig.
        """
        # Converte para float/decimal para garantir comparação correta
        gig_price = float(gig_data.get('preco', 0))
        paid_amount = float(amount)

        if paid_amount < gig_price:
            raise ValidationError(
                f"Valor incorreto. O preço do Gig é R$ {gig_price}, mas foi enviado R$ {paid_amount}.")

        return True