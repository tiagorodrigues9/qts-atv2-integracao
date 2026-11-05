# AGENTS.md - Diretrizes de Engenharia e Governança para Agentes de IA

Este documento define os princípios de arquitetura, padrões de projeto e regras de integridade que agentes de IA e desenvolvedores devem seguir ao manter ou estender o projeto **TechCare OS**.

## 1. Princípios Arquiteturais
- **Separação de Responsabilidades**: Modelos de domínio (`models/`), regras de negócio (`services/`), persistência (`repository/`) e camadas de apresentação (`main.py` com rotas web e API) devem permanecer desacoplados.
- **Isolamento de Dependências Externas**: Nenhuma chamada HTTP para serviços remotos de terceiros (como validação de garantia de fabricantes) deve ser executada em testes automatizados. O mock com `mocker.patch` ou injeção de dependência é obrigatório.
- **Idempotência e Estado Limpo**: Todos os testes devem rodar em ambiente limpo. O repositório em memória deve ser resetado no setup e no teardown de cada teste através de fixtures com `yield`.

## 2. Padrões de Teste
- **Padrão AAA (Arrange, Act, Assert)**: Todo teste unitário e de integração deve manter as três fases claramente delimitadas com comentários indicativos.
- **Factory Pattern**: A geração de dados fictícios para testes deve ser centralizada em `tests/factories.py` usando `Faker("pt_BR")`, garantindo que nomes, CPFs, e-mails e equipamentos representem entidades verossímeis.
- **Page Object Model (POM)**: Toda interação nos testes E2E do Playwright deve ser mediada por classes de página (ex: `OrderPage`), encapsulando os seletores semânticos e ações de tela.

## 3. Diretrizes de Acessibilidade (WCAG 2.1 AA)
- Qualquer novo elemento de interface web introduzido nos templates deve ser auditado com Axe-core.
- Violações de acessibilidade (como elementos interativos sem rótulo, contraste insuficiente ou ausência de atributos semânticos) quebram a pipeline de testes (`violations_count == 0`).
- O foco via teclado deve ser garantido com indicador visual claro (`:focus-visible`).

## 4. Gerenciamento e Execução
- Todos os comandos devem ser orquestrados através do gerenciador de pacotes **uv** (`uv run ...`).

