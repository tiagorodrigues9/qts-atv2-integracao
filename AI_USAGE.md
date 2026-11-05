# Relatório de Transparência e Governança no Uso de Inteligência Artificial (AI_USAGE.md)

Este documento apresenta de forma transparente a utilização de ferramentas de Inteligência Artificial generativa durante o desenvolvimento da atividade prática avaliativa da disciplina **Qualidade e Teste de Software (QTS)**, descrevendo seu papel como recurso de apoio, as atividades em que foi empregada e os procedimentos de revisão e validação realizados pelo estudante.

---

## 1. Ferramenta de IA Utilizada

- **Ferramenta:** Google Antigravity (Advanced Agentic Coding Environment).
- **Modelo de Linguagem:** Gemini 3.8 Flash (High Reasoning Mode).
- **Ambiente de Execução:** Windows x64 com Python 3.12.16 gerenciado via `uv`.

---

## 2. Escopo de Utilização da Inteligência Artificial

A ferramenta de Inteligência Artificial foi utilizada como recurso de apoio ao processo de desenvolvimento, atuando como assistente de programação (*Pair Programming Assistant*). Sua utilização ocorreu sob orientação e condução do estudante, que permaneceu responsável pelas decisões técnicas, definição dos requisitos, direcionamento das implementações e avaliação das soluções propostas.

A IA foi empregada como suporte em atividades de consulta técnica, estruturação, elaboração e revisão de código, identificação de possíveis problemas e sugestão de soluções. As implementações realizadas com seu auxílio foram analisadas e verificadas pelo estudante, considerando os objetivos pedagógicos e os requisitos estabelecidos para a atividade.

As principais etapas em que houve utilização da ferramenta foram:

1. **Especificação do Produto e Requisitos Não Funcionais (PRD.md):**
   - Apoio na organização, estruturação e revisão dos requisitos funcionais e não funcionais, considerando as características da norma internacional **ISO/IEC 25010**, incluindo Adequação Funcional, Desempenho, Acessibilidade, Confiabilidade, Segurança, Manutenibilidade e Portabilidade.

2. **Implementação do Sistema Sob Teste (SUT):**
   - Auxílio na estruturação da arquitetura em camadas utilizando FastAPI e modelos tipados com Pydantic v2.
   - Suporte na elaboração e revisão de validações customizadas, incluindo regex de e-mail, formato e comprimento de CPF e validação de preços estritamente positivos.
   - Apoio na implementação e revisão da interface web utilizando HTML5 e CSS3, considerando critérios de acessibilidade e as diretrizes WCAG 2.1 nível AA.

3. **Desenvolvimento da Suíte de Testes:**
   - **Camada de Integração:** Apoio na estruturação dos testes com `TestClient`, seguindo o padrão AAA (Arrange, Act, Assert), utilização de fixtures com ciclo de vida explícito (`setup` e `teardown` via `yield`), isolamento de chamadas à API externa de garantia de fabricantes com `mocker.patch`, contemplando cenários de aprovação, recusa de garantia e falha de rede/timeout 502, além da utilização de Factory sintética com `Faker("pt_BR")`.
   - **Camada End-to-End (E2E):** Auxílio na elaboração e revisão dos testes utilizando o padrão Page Object Model (POM), por meio da classe `OrderPage` e seletores semânticos recomendados pelo Playwright, como `get_by_role`, `get_by_label` e `get_by_text`.
   - **Auditoria de Acessibilidade:** Suporte na configuração e elaboração dos testes automatizados de acessibilidade com o motor Axe-core (`axe-playwright-python`), além da verificação de navegação sequencial por teclado utilizando `page.keyboard.press("Tab")` e `expect().to_be_focused()`.
   - **Testes de Carga:** Apoio na elaboração e revisão do script `locustfile.py`, utilizando tarefas ponderadas (`@task`) para simular múltiplos usuários concorrentes.

---

## 3. Processo de Revisão Técnica, Auditoria Humana e Resolução de Anomalias

Durante o desenvolvimento e a execução da aplicação, as sugestões e implementações produzidas com auxílio da IA foram submetidas à análise e verificação técnica pelo estudante. Esse processo envolveu a identificação de inconsistências, avaliação das soluções propostas, realização de ajustes e execução de testes para verificar o comportamento esperado do sistema.

Entre as situações identificadas durante esse processo, destacam-se:

1. **Auditoria de Assinatura do Framework (FastAPI / Starlette):**
   - *Anomalia Detectada:* Incompatibilidade de argumentos na chamada de `templates.TemplateResponse`, na qual a passagem de um dicionário como segundo argumento gerava o erro `TypeError: unhashable type: 'dict'`.
   - *Intervenção e Correção:* Após a identificação do problema, foi realizada a adequação da chamada para a assinatura compatível com a versão utilizada, empregando parâmetros nomeados (`request=request, name="index.html", context={...}`), restabelecendo a renderização da página.

2. **Auditoria de Seletores no Playwright (Strict Mode Violation):**
   - *Anomalia Detectada:* A asserção `get_by_role("status")` identificava mais de um elemento correspondente, gerando ambiguidade entre uma tag informativa no cabeçalho e o alerta dinâmico de feedback.
   - *Intervenção e Correção:* A semântica dos elementos foi revisada e o seletor foi refinado para identificar de maneira unívoca o alerta responsável por apresentar o resultado da ação do usuário.

3. **Auditoria de Contraste e Acessibilidade (Axe-core):**
   - Foram realizadas verificações automatizadas das regras de acessibilidade WCAG 2.1 AA por meio da biblioteca Axe-core. Os resultados foram analisados considerando elementos como botões, campos de texto, skip link e badges, com atenção aos critérios de contraste mínimo de 4.5:1 e à identificação de possíveis violações.

4. **Validação de Performance sob Carga (Locust):**
   - Foram analisados os resultados dos testes de carga, considerando os percentis de tempo de resposta (`p95` e `p99`) e a taxa de falhas das requisições. Os resultados obtidos foram comparados com as metas de desempenho estabelecidas para a aplicação, utilizando como referência os atributos de qualidade da ISO/IEC 25010.

---

## 4. Declaração de Integridade Acadêmica

O estudante permanece responsável pelo desenvolvimento, pelas decisões técnicas, pela arquitetura, pela documentação e pelos resultados apresentados na atividade.

As sugestões, orientações e implementações produzidas com auxílio da ferramenta de Inteligência Artificial foram submetidas à análise, revisão e validação humana, buscando assegurar sua adequação aos requisitos estabelecidos e aos objetivos pedagógicos da disciplina.

A utilização da ferramenta ocorreu de maneira transparente, reconhecendo seu papel como instrumento de apoio ao processo de desenvolvimento, sem transferir a ela a responsabilidade acadêmica pelo trabalho.

Dessa forma, este documento registra a participação da Inteligência Artificial no processo de desenvolvimento, preservando a responsabilidade do estudante sobre o conteúdo, a qualidade e a integridade dos artefatos entregues.