import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page, expect

from tests.e2e.pages.order_page import OrderPage
from tests.factories import ServiceOrderFactory


@pytest.mark.accessibility
class TestAccessibilityWCAG:
    """Auditoria de Acessibilidade WCAG 2.1 AA e Navegação por Teclado."""

    def test_wcag_21_aa_compliance_empty_state(self, page: Page, live_server_url: str):
        """
        Auditoria automatizada WCAG 2.1 AA com Axe-core na página inicial (estado limpo).
        Verifica regras de contraste, labels de formulário, marcos semânticos e estrutura de cabeçalhos.
        """
        order_page = OrderPage(page, live_server_url)
        order_page.navigate()

        axe = Axe()
        results = axe.run(
            page,
            options={
                "runOnly": {
                    "type": "tag",
                    "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"],
                }
            },
        )

        assert results.violations_count == 0, (
            f"Violações WCAG 2.1 AA detectadas ({results.violations_count}):\n"
            f"{results.generate_report()}"
        )

    def test_wcag_21_aa_compliance_with_populated_table(
        self,
        page: Page,
        live_server_url: str,
        mock_external_warranty_approved,
    ):
        """
        Auditoria automatizada WCAG 2.1 AA com Axe-core na página contendo ordens cadastradas e alerta de feedback.
        Garante que elementos dinâmicos (tabela preenchida e alerta aria-live) mantêm conformidade.
        """
        order_page = OrderPage(page, live_server_url)
        order_page.navigate()

        order_data = ServiceOrderFactory.build_dict()
        order_page.create_order(order_data)

        axe = Axe()
        results = axe.run(
            page,
            options={
                "runOnly": {
                    "type": "tag",
                    "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"],
                }
            },
        )

        assert results.violations_count == 0, (
            f"Violações WCAG 2.1 AA na página preenchida:\n"
            f"{results.generate_report()}"
        )

    def test_keyboard_navigation_tab_order_and_focus(self, page: Page, live_server_url: str):
        """
        Validação de Navegação Exclusiva por Teclado:
        Garante que o usuário consegue navegar sequencialmente usando a tecla Tab,
        atingindo o Skip Link, todos os campos do formulário na ordem correta e o botão de submissão,
        com validação explícita de to_be_focused().
        """
        order_page = OrderPage(page, live_server_url)
        order_page.navigate()

        # 1º Tab -> Skip Link (acessibilidade para pular ao conteúdo)
        page.keyboard.press("Tab")
        expect(order_page.skip_link).to_be_focused()

        # 2º Tab -> Campo Nome Completo
        page.keyboard.press("Tab")
        expect(order_page.name_input).to_be_focused()

        # 3º Tab -> Campo E-mail
        page.keyboard.press("Tab")
        expect(order_page.email_input).to_be_focused()

        # 4º Tab -> Campo Telefone
        page.keyboard.press("Tab")
        expect(order_page.phone_input).to_be_focused()

        # 5º Tab -> Campo CPF
        page.keyboard.press("Tab")
        expect(order_page.cpf_input).to_be_focused()

        # 6º Tab -> Select Tipo de Dispositivo
        page.keyboard.press("Tab")
        expect(order_page.device_type_select).to_be_focused()

        # 7º Tab -> Campo Marca do Dispositivo
        page.keyboard.press("Tab")
        expect(order_page.device_brand_input).to_be_focused()

        # 8º Tab -> Campo Modelo do Dispositivo
        page.keyboard.press("Tab")
        expect(order_page.device_model_input).to_be_focused()

        # 9º Tab -> Campo Número de Série
        page.keyboard.press("Tab")
        expect(order_page.device_serial_input).to_be_focused()

        # 10º Tab -> Campo Descrição do Problema
        page.keyboard.press("Tab")
        expect(order_page.issue_description_input).to_be_focused()

        # 11º Tab -> Campo Valor Estimado
        page.keyboard.press("Tab")
        expect(order_page.estimated_price_input).to_be_focused()

        # 12º Tab -> Botão de Submissão
        page.keyboard.press("Tab")
        expect(order_page.submit_button).to_be_focused()

