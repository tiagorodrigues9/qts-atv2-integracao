import socket
import threading
import time
from typing import Generator
import httpx
import pytest
from fastapi.testclient import TestClient
import uvicorn

from atv2_integracao.main import app
from atv2_integracao.repository.memory_repo import OrderRepository, order_repository
from atv2_integracao.services.external_warranty import ExternalWarrantyClient


def find_free_port() -> int:
    """Obtém uma porta TCP livre dinamicamente para o servidor de teste."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(autouse=True)
def clean_repository() -> Generator[OrderRepository, None, None]:
    """
    Fixture com setup e teardown explícitos via yield.
    Garante o isolamento entre testes limpando o estado do repositório em memória.
    """
    # Setup
    order_repository.clear()

    yield order_repository

    # Teardown
    order_repository.clear()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    Fixture com TestClient para testes de integração de API.
    Utiliza yield para gerenciamento de contexto e teardown.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def live_server_url() -> Generator[str, None, None]:
    """
    Fixture que sobe o servidor FastAPI real em uma thread dedicada para testes E2E e Acessibilidade.
    Realiza healthcheck no setup e encerra graciosamente o servidor no teardown via yield.
    """
    port = find_free_port()
    base_url = f"http://127.0.0.1:{port}"

    config = uvicorn.Config(app=app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config=config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Aguarda o servidor estar pronto (healthcheck)
    start_time = time.time()
    healthy = False
    while time.time() - start_time < 10.0:
        try:
            res = httpx.get(f"{base_url}/health", timeout=1.0)
            if res.status_code == 200:
                healthy = True
                break
        except Exception:
            time.sleep(0.1)

    if not healthy:
        raise RuntimeError("Servidor FastAPI de teste falhou ao inicializar a tempo.")

    yield base_url

    # Teardown
    server.should_exit = True
    thread.join(timeout=3.0)


@pytest.fixture
def mock_external_warranty_approved(monkeypatch):
    """
    Mock padrão do serviço externo retornando sucesso para testes E2E.
    Evita chamadas de rede externas e garante previsibilidade.
    """
    def fake_check(self, serial_number: str, brand: str, estimated_price: float):
        return {
            "status": "APPROVED",
            "authorization_code": "AUTH-TEST-OK-99",
            "message": "Garantia validada com sucesso pelo mock.",
        }

    monkeypatch.setattr(ExternalWarrantyClient, "check_warranty", fake_check)

