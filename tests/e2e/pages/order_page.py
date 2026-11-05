from typing import Any, Dict
from playwright.sync_api import Locator, Page


class OrderPage:
    """
    Page Object Model (POM) representando a página principal do TechCare OS.
    Encapsula interações utilizando seletores semânticos (get_by_role, get_by_label, get_by_text).
    """

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

        # Seletores Semânticos (WCAG e Playwright Best Practices)
        self.skip_link: Locator = self.page.get_by_role("link", name="Pular para o conteúdo principal")
        self.heading: Locator = self.page.get_by_role("heading", name="TechCare OS", level=1)
        self.form_heading: Locator = self.page.get_by_role("heading", name="Abertura de Ordem de Serviço", level=2)
        self.list_heading: Locator = self.page.get_by_role("heading", name="Ordens de Serviço Registradas", level=2)

        # Campos de Formulário acessíveis por Label
        self.name_input: Locator = self.page.get_by_label("Nome Completo")
        self.email_input: Locator = self.page.get_by_label("E-mail")
        self.phone_input: Locator = self.page.get_by_label("Telefone")
        self.cpf_input: Locator = self.page.get_by_label("CPF")
        self.device_type_select: Locator = self.page.get_by_label("Tipo de Dispositivo")
        self.device_brand_input: Locator = self.page.get_by_label("Marca do Dispositivo")
        self.device_model_input: Locator = self.page.get_by_label("Modelo do Dispositivo")
        self.device_serial_input: Locator = self.page.get_by_label("Número de Série")
        self.issue_description_input: Locator = self.page.get_by_label("Descrição do Problema")
        self.estimated_price_input: Locator = self.page.get_by_label("Valor Estimado (R$)")

        # Botão de Envio semântico
        self.submit_button: Locator = self.page.get_by_role("button", name="Cadastrar Ordem de Serviço")

        # Alerta de Feedback
        self.alert_message: Locator = self.page.get_by_role("status")

    def navigate(self) -> None:
        """Navega até a página principal."""
        self.page.goto(f"{self.base_url}/")

    def fill_form(self, order_data: Dict[str, Any]) -> None:
        """Preenche todos os campos do formulário com dados sintéticos."""
        customer = order_data["customer"]
        device = order_data["device"]

        self.name_input.fill(customer["name"])
        self.email_input.fill(customer["email"])
        self.phone_input.fill(customer["phone"])
        self.cpf_input.fill(customer["cpf"])

        self.device_type_select.select_option(device["device_type"])
        self.device_brand_input.fill(device["brand"])
        self.device_model_input.fill(device["model"])
        self.device_serial_input.fill(device["serial_number"])

        self.issue_description_input.fill(order_data["issue_description"])
        self.estimated_price_input.fill(str(order_data["estimated_price"]))

    def submit(self) -> None:
        """Clica no botão de submissão do formulário."""
        self.submit_button.click()

    def create_order(self, order_data: Dict[str, Any]) -> None:
        """Fluxo completo de preenchimento e submissão de ordem de serviço."""
        self.fill_form(order_data)
        self.submit()

    def get_order_row(self, customer_name: str) -> Locator:
        """Localiza a linha da tabela contendo o nome do cliente."""
        return self.page.locator("table tbody tr", has_text=customer_name)

