import os
import httpx


class ExternalServiceException(Exception):
    """Exceção levantada quando há falha de comunicação ou indisponibilidade no serviço externo."""
    pass


class ExternalWarrantyClient:
    """Cliente para integração com API externa de validação de garantia e antifraude."""

    def __init__(self, base_url: str = "https://api.warranty-hub.internal/v1", timeout: float = 3.0):
        self.base_url = base_url
        self.timeout = timeout
        # Modo de simulação opcional para testes de carga e demonstração local
        self.mock_mode = os.getenv("MOCK_EXTERNAL_SERVICE", "false").lower() in ("true", "1", "yes")

    def check_warranty(self, serial_number: str, brand: str, estimated_price: float) -> dict:
        """
        Consulta a API externa de garantia e avaliação de risco.
        Retorna dicionário com status ('APPROVED' ou 'DECLINED') e código de autorização.
        Em caso de erro de rede ou HTTP 5xx, levanta ExternalServiceException.
        """
        if self.mock_mode:
            return {
                "status": "APPROVED",
                "authorization_code": f"AUTH-MOCK-{abs(hash(serial_number)) % 100000:05d}",
                "message": "Garantia validada com sucesso pelo serviço simulado.",
            }

        endpoint = f"{self.base_url}/verify"
        payload = {
            "serial_number": serial_number,
            "brand": brand,
            "estimated_price": estimated_price,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(endpoint, json=payload)
                if response.status_code >= 500:
                    raise ExternalServiceException(f"Serviço externo indisponível: HTTP {response.status_code}")
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as exc:
            raise ExternalServiceException(f"Erro de conexão com o serviço externo: {str(exc)}") from exc
