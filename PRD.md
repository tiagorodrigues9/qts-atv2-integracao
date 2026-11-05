# PRD - Documento de Requisitos do Produto (Product Requirements Document)

## 1. Visão Geral do Produto
O **TechCare OS** é um sistema web moderno e robusto voltado para a **Gestão de Ordens de Serviço (OS) e Validação de Garantia de Equipamentos Eletrônicos** (smartphones, notebooks, tablets e smartwatches). O sistema foi concebido para atender às demandas de laboratórios de assistência técnica autorizada, realizando a triagem de clientes e aparelhos com integração a serviços externos de verificação de garantia de fabricantes e antifraude.

A aplicação foi desenvolvida em **Python 3.12+** utilizando o framework **FastAPI**, validação de esquemas com **Pydantic v2**, renderização web server-side com **Jinja2** e gerenciamento de dependências através do **uv**.

---

## 2. Arquitetura e Especificação de Rotas (API e Web)

### 2.1 Interface Web (HTML)
- `GET /`: Renderiza a página principal contendo o painel de ordens de serviço cadastradas e o formulário de abertura de nova OS.
- `POST /orders`: Recebe os dados de submissão do formulário web (`multipart/form-data`), valida os campos com Pydantic, aciona o serviço de garantia externa e renderiza a página com mensagem de feedback contextualizada (`role="status"`).

### 2.2 Endpoints REST API (JSON)
- `GET /health`: Checagem de integridade do serviço (retorna `{ "status": "healthy", "service": "TechCare OS" }`).
- `GET /api/orders`: Retorna a lista completa de ordens de serviço cadastradas, ordenadas de forma decrescente por ID.
- `POST /api/orders`: Criação programática de uma ordem de serviço.
  - **Payload de Entrada**:
    ```json
    {
      "customer": {
        "name": "Maria Souza Silva",
        "email": "maria.silva@email.com",
        "phone": "11987654321",
        "cpf": "12345678901"
      },
      "device": {
        "device_type": "Smartphone",
        "brand": "Apple",
        "model": "iPhone 15 Pro",
        "serial_number": "SN-APL992819"
      },
      "issue_description": "Aparelho não liga após atualização de firmware.",
      "estimated_price": 450.00
    }
    ```
  - **Respostas Esperadas**:
    - `HTTP 201 Created`: Ordem criada com sucesso (com status `APROVADO` ou `REJEITADO` dependendo do parecer da garantia).
    - `HTTP 422 Unprocessable Entity`: Erro de validação dos dados de entrada (CPF inválido, e-mail malformatado ou preço <= 0).
    - `HTTP 502 Bad Gateway`: Falha de conectividade ou indisponibilidade no serviço externo de garantia.
- `GET /api/orders/{order_id}`: Retorna os detalhes de uma ordem específica.
  - `HTTP 200 OK`: Dados da ordem encontrada.
  - `HTTP 404 Not Found`: Mensagem de erro caso o ID não exista.

---

## 3. Especificação da Interface Web e Acessibilidade

A interface web foi desenhada seguindo as diretrizes de acessibilidade **WCAG 2.1 nível AA**:
1. **Perceptível**:
   - Razão de contraste mínima de 4.5:1 para textos regulares e 7:1 para botões primários.
   - Atributo `lang="pt-BR"` declarado explicitamente no elemento raiz `<html>`.
   - Elemento `<title>` dinâmico e semântico em todas as telas.
2. **Operável**:
   - Mecanismo de Skip Link (`<a href="#conteudo-principal" class="skip-link">Pular para o conteúdo principal</a>`) como primeiro elemento interativo.
   - Navegabilidade 100% via teclado: foco visível com anel de foco destacado (`:focus-visible` com 3px de contorno e contraste elevado).
   - Ordem lógica e contínua do tabulador (`Tab` order) percorrendo Skip Link -> Dados do Cliente -> Equipamento -> Orçamento -> Botão de Submissão.
3. **Compreensível**:
   - Todos os campos de formulário possuem `<label for="...">` explicitamente associados com `id` correspondente.
   - Mensagens de feedback e alertas com atributos `role="status"` e `aria-live="polite"`.
4. **Robusto**:
   - Estrutura semântica HTML5 com marcos adequados: `<header role="banner">`, `<main id="conteudo-principal" role="main">`, `<footer role="contentinfo">`, `<section aria-labelledby="...">`.

---

## 4. Requisitos Não Funcionais (ISO/IEC 25010)

| Característica ISO/IEC 25010 | Subcaracterística | Especificação no TechCare OS | Critério de Aceitação / Validação |
|---|---|---|---|
| **Adequação Funcional** | Completude e Correção | Gestão completa de ordens de serviço com validação de garantia. | 100% dos fluxos de negócio testados via integração e E2E. |
| **Eficiência de Desempenho** | Comportamento Temporal | Resposta rápida sob carga de usuários concorrentes. | Tempo de resposta p95 < 100ms e vazão > 50 RPS com 25 usuários no Locust. |
| **Usabilidade** | Acessibilidade | Conformidade estrita com padrões internacionais de acessibilidade digital. | **0 violações** na auditoria automatizada WCAG 2.1 AA com Axe-core (`axe-playwright-python`). |
| **Usabilidade** | Operabilidade | Operabilidade completa por usuários que dependem exclusivamente de teclado. | Navegação por `Tab` validada com `to_be_focused()` no Playwright. |
| **Confiabilidade** | Tolerância a Falhas | Resiliência contra quedas da API externa de garantia de fabricantes. | Resposta HTTP 502 padronizada em caso de timeout/falha de rede, sem derrubar a aplicação. |
| **Segurança** | Integridade dos Dados | Proteção contra entrada de dados maliciosos ou corrompidos. | Schemas Pydantic com validação rigorosa de tipos, CPFs (11 dígitos) e valores numéricos positivos. |
| **Manutenibilidade** | Modularidade e Testabilidade | Código desacoplado e coberto por testes em múltiplos níveis da pirâmide. | Padrões Factory (Faker pt_BR), Page Object Model (POM), Mocks (pytest-mock) e padrão AAA. |
| **Portabilidade** | Facilidade de Instalação | Execução consistente e reproduzível em qualquer ambiente moderno. | Gerenciamento via `uv` com Python 3.12+ e arquivo `pyproject.toml`. |

