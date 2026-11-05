import random
from locust import HttpUser, task, between
from faker import Faker

faker = Faker("pt_BR")


class TechCareUser(HttpUser):
    """
    Simulação de usuários concorrentes interagindo com o sistema TechCare.
    Cobre fluxos de navegação web, consultas de API e criação de ordens de serviço.
    """
    # Tempo de espera entre requisições (0.1 a 0.5 segundos)
    wait_time = between(0.1, 0.5)

    def on_start(self):
        """Inicialização do contexto do usuário virtual."""
        self.created_order_ids = []

    @task(4)
    def load_home_page(self):
        """Simula acesso à página web HTML (Dashboard / Abertura de OS)."""
        self.client.get("/", name="[WEB] Carregar Página Principal")

    @task(3)
    def list_orders(self):
        """Simula consulta à listagem de ordens de serviço via API REST."""
        res = self.client.get("/api/orders", name="[API] Listar Ordens de Serviço")
        if res.status_code == 200:
            orders = res.json()
            if orders and isinstance(orders, list):
                self.created_order_ids = [o["id"] for o in orders[:10]]

    @task(2)
    def create_order(self):
        """Simula submissão de nova ordem de serviço com dados sintéticos."""
        clean_cpf = "".join(str(random.randint(0, 9)) for _ in range(11))
        payload = {
            "customer": {
                "name": faker.name(),
                "email": faker.ascii_safe_email(),
                "phone": "11987654321",
                "cpf": clean_cpf,
            },
            "device": {
                "device_type": random.choice(["Smartphone", "Notebook", "Tablet"]),
                "brand": random.choice(["Apple", "Samsung", "Dell", "Lenovo"]),
                "model": "Aparelho Carga 2026",
                "serial_number": f"SN-{random.randint(1000000, 9999999)}",
            },
            "issue_description": "Teste de carga: manutenção de bateria e sistema de arrefecimento.",
            "estimated_price": round(random.uniform(180.0, 1500.0), 2),
        }

        with self.client.post("/api/orders", json=payload, name="[API] Criar Ordem de Serviço", catch_response=True) as response:
            if response.status_code in (201, 200):
                data = response.json()
                if "id" in data:
                    self.created_order_ids.append(data["id"])
                response.success()
            else:
                response.failure(f"Status inesperado: {response.status_code}")

    @task(1)
    def get_order_details(self):
        """Simula consulta detalhada de uma ordem específica pelo ID."""
        order_id = random.choice(self.created_order_ids) if self.created_order_ids else 1
        self.client.get(f"/api/orders/{order_id}", name="[API] Consultar Ordem por ID")

