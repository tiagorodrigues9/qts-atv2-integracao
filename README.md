# TechCare OS - Gestão de Ordens de Serviço & Garantia de Dispositivos

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Package Manager](https://img.shields.io/badge/uv-fast%20python%20manager-purple.svg)](https://docs.astral.sh/uv/)
[![Framework](https://img.shields.io/badge/FastAPI-0.162%2B-teal.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/pytest-14%20passed%20(100%25)-brightgreen.svg)]()
[![Accessibility](https://img.shields.io/badge/WCAG%202.1%20AA-0%20violations-success.svg)]()
[![Performance](https://img.shields.io/badge/Locust%20p95-27ms%20%7C%2067.5%20RPS-blue.svg)]()

Trabalho prático individual da disciplina **Qualidade e Teste de Software (QTS)** - FATEC.  
Consolidação prática dos níveis intermediário e superior da **Pirâmide de Testes** e dos requisitos não funcionais da norma **ISO/IEC 25010**.

---

## 1. Visão Geral do Sistema (SUT)

O **TechCare OS** é uma aplicação web completa desenvolvida com **FastAPI** e validação estrita via **Pydantic v2**, voltada para triagem, abertura e acompanhamento de Ordens de Serviço (OS) em assistências técnicas e laboratórios de reparo de dispositivos (Smartphones, Notebooks, Tablets e Smartwatches).

### Principais Destaques Arquiteturais:
- **Isolamento de Serviços Externos**: Integração com API externa simulada de validação de garantia de fabricantes e análise antifraude (`ExternalWarrantyClient`), com tratamento resiliente de falhas (`HTTP 502 Bad Gateway`).
- **Padrão AAA (Arrange, Act, Assert)**: Todos os testes de integração estruturados com separação clara de responsabilidades.
- **Factory Pattern com Faker Brasil**: Geração determinística de dados sintéticos verossímeis (`faker.Faker("pt_BR")`) para nomes, CPFs de 11 dígitos, telefones e dispositivos.
- **Page Object Model (POM)**: Testes ponta a ponta com Playwright encapsulados na classe `OrderPage` utilizando estritamente **seletores semânticos acessíveis** (`get_by_role`, `get_by_label`, `get_by_text`).
- **Acessibilidade WCAG 2.1 AA**: Auditoria automatizada com **Axe-core** (`axe-playwright-python`) resultando em **0 violações**, com Skip Link, alto contraste de cores e validação de fluxo exclusivo por teclado (`Tab` e `to_be_focused()`).
- **Testes de Carga com Locust**: Avaliação de performance e vazão sob múltiplos usuários concorrentes.

---

## 2. Estrutura do Repositório

```text
ATV2-integracao/
├── .cursorrules               # Regras de contexto e diretrizes para agentes de IA
├── AGENTS.md                  # Princípios de arquitetura e qualidade para assistentes de IA
├── AI_USAGE.md                # Relatório de transparência, governança e auditoria da IA
├── PRD.md                     # Documento de Requisitos do Produto e ISO/IEC 25010
├── README.md                  # Instruções de execução, métricas e roteiro do vídeo
├── pyproject.toml             # Configuração do projeto uv, dependências e pytest
├── locustfile.py              # Script de teste de carga com Locust (HttpUser)
├── src/
│   └── atv2_integracao/
│       ├── __init__.py
│       ├── main.py            # Servidor FastAPI com rotas web e REST API
│       ├── models/
│       │   ├── __init__.py
│       │   └── order.py       # Modelos Pydantic (Customer, Device, ServiceOrder)
│       ├── services/
│       │   ├── __init__.py
│       │   ├── external_warranty.py  # Cliente do serviço externo de garantia
│       │   └── order_service.py      # Regras de negócio da aplicação
│       ├── repository/
│       │   ├── __init__.py
│       │   └── memory_repo.py # Repositório thread-safe em memória
│       ├── templates/
│       │   ├── base.html      # Layout base acessível com Skip Link e Landmarks
│       │   └── index.html     # Painel de ordens e formulário semântico
│       └── static/
│           └── css/
│               └── style.css  # Folha de estilo WCAG 2.1 AA (contraste > 4.5:1)
└── tests/
    ├── __init__.py
    ├── conftest.py            # Fixtures (clean_repository, client, live_server_url)
    ├── factories.py           # Factory Pattern com Faker("pt_BR")
    ├── integration/
    │   ├── __init__.py
    │   └── test_orders_api.py # Testes de integração (AAA, mocks de sucesso e falha)
    ├── e2e/
    │   ├── __init__.py
    │   ├── pages/
    │   │   ├── __init__.py
    │   │   └── order_page.py  # Page Object Model com seletores semânticos
    │   └── test_order_flows.py# Fluxos ponta a ponta com Playwright
    └── accessibility/
        ├── __init__.py
        └── test_accessibility.py # Auditoria WCAG 2.1 AA (Axe-core) e foco por teclado
```

---

## 3. Guia de Instalação e Execução com `uv`

### 3.1 Pré-requisitos
- **Python 3.12+**
- **uv** instalado ([Instalação do uv](https://docs.astral.sh/uv/))

### 3.2 Sincronização de Dependências
Clone o repositório e sincronize o ambiente virtual:
```bash
# Sincroniza todas as dependências declaradas no pyproject.toml
uv sync

# Instala os binários do Chromium necessários para o Playwright
uv run playwright install chromium
```

### 3.3 Execução da Aplicação Web
Para iniciar o servidor Uvicorn com hot-reload ativo:
```bash
uv run uvicorn src.atv2_integracao.main:app --reload --port 8000
```
- Acesse a interface web: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Acesse a documentação interativa OpenAPI/Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 4. Execução da Suíte de Testes Automatizados

A suíte possui **14 testes automatizados** cobrindo todos os níveis exigidos:

### 4.1 Testes de Integração (Fixtures, Mocks e Faker)
Executa a validação de status HTTP, payloads no padrão AAA e isolamento com `mocker.patch`:
```bash
uv run pytest -m integration -v
```

### 4.2 Testes End-to-End (E2E) com Playwright e Page Object Model
Executa os fluxos de interface com validação semântica em navegador real:
```bash
uv run pytest -m e2e -v
```

### 4.3 Auditoria de Acessibilidade (Axe-core WCAG 2.1 AA e Teclado)
Executa a auditoria automatizada de 0 violações e a verificação de ordem de tabulação e foco:
```bash
uv run pytest -m accessibility -v
```

### 4.4 Execução da Suíte Completa
Executa todos os 14 testes de uma única vez:
```bash
uv run pytest -v
```

Resultado esperado:
```text
======================= 14 passed in 3.43s =======================
```

---

## 5. Testes de Carga e Performance (Locust)

O teste de carga simula múltiplos usuários concorrentes realizando leituras da página web, listagens na API REST, criação de ordens de serviço com dados sintéticos e consultas por ID.

### 5.1 Como Executar o Teste de Carga

Em um terminal, inicie a aplicação habilitando a simulação de garantia:
```bash
# No Windows PowerShell:
$env:MOCK_EXTERNAL_SERVICE="true"; uv run uvicorn src.atv2_integracao.main:app --port 8000
```

Em outro terminal, execute o Locust em modo headless por 15 segundos com 25 usuários concorrentes:
```bash
uv run locust --headless -u 25 -r 5 --run-time 15s --host http://127.0.0.1:8000 --csv=benchmark
```

*(Ou execute `uv run locust` sem `--headless` para abrir a interface gráfica do Locust em [http://localhost:8089](http://localhost:8089)).*

### 5.2 Métricas Consolidadas Obtidas no Benchmark

A tabela abaixo registra os dados consolidados obtidos no benchmark de carga com **25 usuários concorrentes**:

| Métrica Avaliada | Valor Obtido | Critério de Aceitação (ISO/IEC 25010) | Status |
|---|---|---|---|
| **Total de Requisições** | **880 a 902 requisições** | Conclusão sem travamentos | APROVADO |
| **Requisições por Segundo (RPS)** | **67.52 req/s** | RPS > 50.0 req/s | APROVADO |
| **Taxa de Falhas (Failures)** | **0.00% (0 falhas)** | Falhas < 1.0% | APROVADO |
| **Tempo de Resposta Médio** | **9.34 ms** | Tempo médio < 50 ms | APROVADO |
| **Tempo de Resposta Mediano (50%)** | **6.00 ms** | Mediana < 30 ms | APROVADO |
| **Tempo de Resposta p90** | **18.00 ms** | p90 < 100 ms | APROVADO |
| **Tempo de Resposta p95** | **27.00 ms** | p95 < 200 ms | APROVADO |
| **Tempo de Resposta p99** | **71.00 ms** | p99 < 300 ms | APROVADO |
| **Tempo de Resposta Mínimo / Máximo** | **1.92 ms / 106.55 ms** | Estabilidade de latência | APROVADO |

#### Detalhamento por Operação (Percentil 95%):
- `[API] Consultar Ordem por ID`: **p95 = 15 ms** (RPS: 7.52)
- `[API] Criar Ordem de Serviço`: **p95 = 27 ms** (RPS: 12.58)
- `[API] Listar Ordens de Serviço`: **p95 = 33 ms** (RPS: 18.49)
- `[WEB] Carregar Página Principal`: **p95 = 25 ms** (RPS: 28.92)

---

## 6. Governança de Inteligência Artificial

Em conformidade com as exigências pedagógicas e de integridade acadêmica:
- **[PRD.md](PRD.md)**: Especificação detalhada de rotas, interface e mapeamento dos requisitos não funcionais sob a norma **ISO/IEC 25010**.
- **[.cursorrules](.cursorrules)** e **[AGENTS.md](AGENTS.md)**: Regras de contexto, padrões de projeto, diretrizes de acessibilidade e isolamento de dependências externas.
- **[AI_USAGE.md](AI_USAGE.md)**: Relatório de transparência detalhando o papel da IA (Antigravity com Gemini 3.8 Flash), metodologia de auditoria humana e anomalias corrigidas durante o desenvolvimento.
