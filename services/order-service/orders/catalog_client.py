import requests
from rest_framework.exceptions import ValidationError


class CatalogClient:
    # URL interna do Docker (nome do serviço no docker-compose)
    BASE_URL = "http://catalog-service:8000/api/catalog"

    @classmethod
    def get_gig_details(cls, gig_id):
        """
        Consulta o Catalog Service para pegar detalhes do Gig (inclui os pacotes).
        """
        try:
            url = f"{cls.BASE_URL}/servicos/by-id/{gig_id}/"
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
    def get_pacote(cls, gig_data, pacote_id):
        """
        Procura o Pacote escolhido dentro dos pacotes do Gig retornado pelo catálogo.
        O preço cobrado sempre vem daqui — nunca é aceito do cliente.
        """
        for pacote in gig_data.get('pacotes', []):
            if pacote.get('id') == pacote_id:
                return pacote

        raise ValidationError(f"Pacote {pacote_id} não encontrado para este Gig.")
