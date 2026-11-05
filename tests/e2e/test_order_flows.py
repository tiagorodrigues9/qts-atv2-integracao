import pytest
from playwright.sync_api import Page, expect

from tests.e2e.pages.order_page import OrderPage
from tests.factories import ServiceOrderFactory


@pytest.mark.e2e
class TestOrderFlowsE2E:
    """Testes de ponta a ponta (E2E) com Playwright e Page Object Model."""

    def test_user_can_view_home_page_and_empty_state(self, page: Page, live_server_url: str):
        """Valida que a página inicial carrega corretamente com seus elementos semânticos."""
        order_page = OrderPage(page, live_server_url)

        order_page.navigate()

        expect(order_page.heading).to_be_visible()
        expect(order_page.form_heading).to_be_visible()
        expect(order_page.list_heading).to_be_visible()
        expect(page.get_by_text("Nenhuma ordem de serviço cadastrada no momento.")).to_be_visible()

    def test_user_can_submit_valid_order_and_see_in_table(
        self,
        page: Page,
        live_server_url: str,
        mock_external_warranty_approved,
    ):
        """
        Fluxo E2E Completo:
        O usuário preenche o formulário de abertura de OS e submete.
        A aplicação deve processar, exibir o alerta de sucesso e listar a OS na tabela com status APROVADO.
        """
        order_page = OrderPage(page, live_server_url)
        order_page.navigate()

        # Dados sintéticos brasileiros via Factory
        fake_data = ServiceOrderFactory.build_dict(
            customer_kwargs={"name": "Beatriz Alcantara"},
            device_kwargs={"device_type": "Notebook", "brand": "Dell", "model": "XPS 13"},
            issue_description="Tela piscando em tons verdes e falha na porta USB-C.",
            estimated_price=890.00,
        )

        # Preenche e envia via Page Object Model
        order_page.create_order(fake_data)

        # Asserções no padrão AAA
        expect(order_page.alert_message).to_be_visible()
        expect(order_page.alert_message).to_contain_text("cadastrada com sucesso! Status: APROVADO.")

        # Linha na tabela com os dados cadastrados
        order_row = order_page.get_order_row("Beatriz Alcantara")
        expect(order_row).to_be_visible()
        expect(order_row).to_contain_text("Dell XPS 13")
        expect(order_row).to_contain_text("APROVADO")
        expect(order_row).to_contain_text("AUTH-TEST-OK-99")

    def test_user_submits_order_with_declined_warranty(
        self,
        page: Page,
        live_server_url: str,
        monkeypatch,
    ):
        """
        Fluxo E2E com Recusa de Garantia:
        Valida que a interface reflete adequadamente a recusa da garantia externa.
        """
        from atv2_integracao.services.external_warranty import ExternalWarrantyClient

        monkeypatch.setattr(
            ExternalWarrantyClient,
            "check_warranty",
            lambda self, serial_number, brand, estimated_price: {
                "status": "DECLINED",
                "authorization_code": None,
                "message": "Equipamento fora do prazo de garantia de fábrica.",
            },
        )

        order_page = OrderPage(page, live_server_url)
        order_page.navigate()

        fake_data = ServiceOrderFactory.build_dict(
            customer_kwargs={"name": "Lucas Gabriel Ferreira"},
            device_kwargs={"device_type": "Smartphone", "brand": "Samsung", "model": "Galaxy A10"},
        )

        order_page.create_order(fake_data)

        order_row = order_page.get_order_row("Lucas Gabriel Ferreira")
        expect(order_row).to_be_visible()
        expect(order_row).to_contain_text("REJEITADO")
        expect(order_row).to_contain_text("Equipamento fora do prazo de garantia")

