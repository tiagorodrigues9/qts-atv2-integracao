import pytest
from fastapi.testclient import TestClient

from atv2_integracao.models.order import OrderStatus
from atv2_integracao.services.external_warranty import ExternalServiceException
from tests.factories import CustomerFactory, DeviceFactory, ServiceOrderFactory


@pytest.mark.integration
class TestOrdersApiIntegration:
    """Suíte de testes de integração da API de Ordens de Serviço (AAA Pattern)."""

    def test_create_order_success_external_mock_approved(self, client: TestClient, mocker):
        """
        Cenário de Sucesso:
        O serviço externo valida e aprova a garantia do equipamento.
        A API deve persistir a OS e retornar HTTP 201 com status APROVADO.
        """
        # [ARRANGE]
        # Massa sintética brasileira gerada via Factory (Faker pt_BR)
        order_payload = ServiceOrderFactory.build_dict(
            customer_kwargs={"name": "Carlos Eduardo Pereira"},
            device_kwargs={"brand": "Apple", "model": "iPhone 15 Pro Max"},
            estimated_price=450.00,
        )

        # Isolamento de dependência externa com Mock (pytest-mock / mocker.patch)
        mock_external = mocker.patch(
            "atv2_integracao.services.order_service.ExternalWarrantyClient.check_warranty",
            return_value={
                "status": "APPROVED",
                "authorization_code": "AUTH-APPLE-778899",
                "message": "Garantia de fábrica ativa. Cobertura total confirmada.",
            },
        )

        # [ACT]
        response = client.post("/api/orders", json=order_payload)

        # [ASSERT]
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["order_number"] == "OS-2026-0001"
        assert data["customer"]["name"] == "Carlos Eduardo Pereira"
        assert data["device"]["brand"] == "Apple"
        assert data["status"] == OrderStatus.APROVADO.value
        assert data["external_validation_code"] == "AUTH-APPLE-778899"
        assert "Garantia de fábrica ativa" in data["validation_message"]

        # Verifica se o mock foi invocado com os parâmetros corretos
        mock_external.assert_called_once_with(
            serial_number=order_payload["device"]["serial_number"],
            brand="Apple",
            estimated_price=450.00,
        )

    def test_create_order_failure_external_mock_declined(self, client: TestClient, mocker):
        """
        Cenário de Falha de Negócio Externa:
        O serviço externo recusa a garantia do dispositivo por ter expirado o prazo.
        A API deve registrar a OS com status REJEITADO e HTTP 201.
        """
        # [ARRANGE]
        order_payload = ServiceOrderFactory.build_dict(
            customer_kwargs={"name": "Mariana Souza Costa"},
            device_kwargs={"brand": "Samsung", "model": "Galaxy S20"},
            estimated_price=320.00,
        )

        mock_external = mocker.patch(
            "atv2_integracao.services.order_service.ExternalWarrantyClient.check_warranty",
            return_value={
                "status": "DECLINED",
                "authorization_code": None,
                "message": "Garantia de fábrica expirada em 15/01/2023.",
            },
        )

        # [ACT]
        response = client.post("/api/orders", json=order_payload)

        # [ASSERT]
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == OrderStatus.REJEITADO.value
        assert data["external_validation_code"] is None
        assert "Garantia de fábrica expirada" in data["validation_message"]
        mock_external.assert_called_once()

    def test_create_order_external_service_network_timeout(self, client: TestClient, mocker):
        """
        Cenário de Falha Crítica de Conectividade Externa:
        O serviço externo de garantia está inacessível ou sofre timeout de rede.
        A API deve tratar a exceção e responder com HTTP 502 Bad Gateway amigável.
        """
        # [ARRANGE]
        order_payload = ServiceOrderFactory.build_dict()

        mocker.patch(
            "atv2_integracao.services.order_service.ExternalWarrantyClient.check_warranty",
            side_effect=ExternalServiceException("Timeout de 3.0s excedido ao conectar com warranty-hub.internal"),
        )

        # [ACT]
        response = client.post("/api/orders", json=order_payload)

        # [ASSERT]
        assert response.status_code == 502
        data = response.json()
        assert "Falha na comunicação com o serviço externo de garantia" in data["detail"]
        assert "Timeout de 3.0s excedido" in data["detail"]

    def test_get_order_by_id_success(self, client: TestClient, mocker):
        """
        Cenário de Consulta por ID:
        Busca uma ordem previamente cadastrada e valida os dados retornados.
        """
        # [ARRANGE]
        mocker.patch(
            "atv2_integracao.services.order_service.ExternalWarrantyClient.check_warranty",
            return_value={"status": "APPROVED", "authorization_code": "AUTH-OK-01"},
        )
        create_resp = client.post("/api/orders", json=ServiceOrderFactory.build_dict())
        created_id = create_resp.json()["id"]

        # [ACT]
        response = client.get(f"/api/orders/{created_id}")

        # [ASSERT]
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_id
        assert data["order_number"] == f"OS-2026-{created_id:04d}"

    def test_get_order_not_found(self, client: TestClient):
        """
        Cenário de Consulta de Ordem Inexistente:
        Tenta buscar um ID inexistente e valida o retorno HTTP 404.
        """
        # [ARRANGE]
        non_existent_id = 9999

        # [ACT]
        response = client.get(f"/api/orders/{non_existent_id}")

        # [ASSERT]
        assert response.status_code == 404
        assert response.json()["detail"] == "Ordem de serviço não encontrada"

    def test_list_orders_empty_and_populated(self, client: TestClient, mocker):
        """
        Cenário de Listagem Geral:
        Valida o retorno inicial de lista vazia e posterior com múltiplos registros.
        """
        # [ARRANGE - Parte 1: Repositório limpo]
        # [ACT]
        initial_resp = client.get("/api/orders")
        # [ASSERT]
        assert initial_resp.status_code == 200
        assert initial_resp.json() == []

        # [ARRANGE - Parte 2: Inserção de 2 ordens com Faker]
        mocker.patch(
            "atv2_integracao.services.order_service.ExternalWarrantyClient.check_warranty",
            return_value={"status": "APPROVED", "authorization_code": "AUTH-LIST"},
        )
        client.post("/api/orders", json=ServiceOrderFactory.build_dict())
        client.post("/api/orders", json=ServiceOrderFactory.build_dict())

        # [ACT]
        populated_resp = client.get("/api/orders")

        # [ASSERT]
        assert populated_resp.status_code == 200
        orders_list = populated_resp.json()
        assert len(orders_list) == 2

    def test_create_order_validation_error_invalid_cpf(self, client: TestClient):
        """
        Cenário de Validação Pydantic:
        Tentativa de envio de CPF com quantidade incorreta de dígitos.
        A API deve responder com HTTP 422 Unprocessable Entity.
        """
        # [ARRANGE]
        invalid_payload = ServiceOrderFactory.build_dict(
            customer_kwargs={"cpf": "123"}  # Menos de 11 dígitos
        )

        # [ACT]
        response = client.post("/api/orders", json=invalid_payload)

        # [ASSERT]
        assert response.status_code == 422
        data = response.json()
        assert any("CPF deve conter exatamente 11 dígitos" in err.get("msg", "") for err in data["detail"])

    def test_create_order_validation_error_negative_price(self, client: TestClient):
        """
        Cenário de Validação Pydantic:
        Tentativa de envio de valor estimado negativo ou zero.
        A API deve responder com HTTP 422 Unprocessable Entity.
        """
        # [ARRANGE]
        invalid_payload = ServiceOrderFactory.build_dict(estimated_price=-50.0)

        # [ACT]
        response = client.post("/api/orders", json=invalid_payload)

        # [ASSERT]
        assert response.status_code == 422
        data = response.json()
        assert any("greater than 0" in err.get("msg", "") for err in data["detail"])

