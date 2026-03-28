## Fase 1: Setup, Estrutura Base e Arquitetura Limpa
**Contexto Inicial Obrigatório:** Antes de gerar qualquer código, leia atentamente as diretrizes em `.github/copilot/instrucoes-gerais.md`. A sua execução deve ser estritamente guiada pelas regras (CBVs, Terminologia Entradas/Saídas, Premium Dark) e skills definidos.

**Objetivo:** Inicializar o projeto "FinTrack" (equipe JRD Labs) configurando a Arquitetura Limpa e criar a fundação do Dashboard utilizando HTMX (Lazy Loading) e ApexCharts para visualizações financeiras premium.

**Tarefas para o @backend:**
1. Crie a estrutura inicial do projeto Django com os apps: `core` (configurações gerais), `finances` (domínio de transações) e `dashboard` (apresentação). Sem uso de DRF ou Docker.
2. Implemente o alicerce da Arquitetura Limpa: crie arquivos `services.py` (para CUD) e `selectors.py` (para consultas/Read) dentro dos apps. **Nenhuma query complexa no `views.py`**.
3. No `selectors.py` do app `dashboard`, crie os métodos que retornarão dicionários para o ApexCharts:
   - `obter_dados_evolucao_6_meses(user)`: Agrupa Entradas e Saídas dos últimos 6 meses (use o ORM `TruncMonth`, `Sum`).
   - `obter_distribuicao_saidas_mes(user)`: Agrupa o total de Saídas do mês atual por categoria.
   - `obter_dados_metas(user)` e `obter_dados_investimentos(user)`: Como os modelos ainda não existem, retorne dados mockados/fictícios para renderizar os gráficos iniciais.
4. No `views.py` do app `dashboard`, crie CBVs para as rotas HTMX separadas (ex: `GraficoEvolucaoView`, `GraficoSaidasView`, `GraficoMetasView`, `GraficoInvestimentosView`). Elas devem apenas chamar o `selectors.py` e retornar fragmentos HTML com o `<script>` do ApexCharts.

**Tarefas para o @frontend e @htmx:**
1. Crie o template principal do Dashboard. Use HTMX para carregar os gráficos de forma assíncrona (ex: `<div hx-get="{% url 'dashboard:grafico_evolucao' %}" hx-trigger="load">Carregando gráfico...</div>`).
2. **Design Visual (ApexCharts via CDN):**
   - Configure o ApexCharts com o tema dark (`theme: { mode: 'dark' }`) e fundo transparente (`background: 'transparent'`).
   - **Gráfico 1 (Evolução):** Tipo `area` com `curve: 'smooth'`. Entradas em verde (`#4ADE80`), Saídas em vermelho/rosa (`#F87171`). Preenchimento com gradiente (`fill: { type: 'gradient' }`).
   - **Gráficos 2, 3 e 4 (Donuts):** Tipo `donut` para Saídas, Metas. Desabilite as bordas (`stroke: { show: false }`).
3. **UI/UX Premium Dark:** Envolva as divs dos gráficos em cards baseados no nosso design system: fundo `bg-slate-800`, `rounded-2xl`, borda sutil `border border-slate-700/50`, `shadow-xl` e `p-6`.

**Tarefas para o @testes e Ação Final (@readme):**
1. Crie os testes automatizados básicos (pytest) para garantir que a infraestrutura e as rotas HTMX estão respondendo HTTP 200.
2. Execute a suíte de testes. Crie o `README.md` curador para o time detalhando: instruções exatas para rodar o projeto, a explicação da Clean Architecture adotada, e como o Lazy Loading com HTMX foi estruturado para otimizar o Dashboard.

## Fase 1.5: Landing Page , Apresentação do Produto e Telas de Autenticação 

**Contexto Inicial Obrigatório:** Leia rigorosamente o arquivo `.github/copilot/instrucoes-gerais.md`. O foco desta fase é implementar a porta de entrada da aplicação e o fluxo de autenticação, usando um design system "Premium Dark" com Glassmorphism.

**Objetivo:** Criar a Landing Page (`/`) e as páginas de Login e Cadastro, replicando fielmente uma interface moderna, escura e com efeitos de desfoque, usando Tailwind CSS puro, Alpine.js para interações simples e CBVs do Django.

**Tarefas para o @backend:**
1. No app `core`, crie uma CBV (`TemplateView`) chamada `LandingPageView` apontando para `core/landing_page.html`.
2. Configure a URL raiz (`/`) no arquivo `urls.py` principal para carregar essa view.
3. Crie um novo app chamado `accounts` (adicione ao `INSTALLED_APPS`).
4. No app `accounts`, crie o `urls.py` (`app_name = 'accounts'`).
5. Configure as CBVs de autenticação: use `LoginView` e `LogoutView` nativas do Django, e crie uma `RegisterView` (herdando de `CreateView` com `UserCreationForm`). O `success_url` do registro deve redirecionar para o login. Defina `LOGIN_REDIRECT_URL` no `settings.py` (pode apontar temporariamente para `/`).

**Tarefas para o @frontend (Especificação Visual Rigorosa):**
O `body` de todas as páginas deve ser `bg-zinc-950 text-zinc-50`. Adicione Alpine.js via CDN.

**1. CSS Customizado (no `<style>` ou arquivo base):**
- Crie a classe `.glass`: `background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.1);`
- Crie `.gradient-text`: texto transparente com `background-clip: text` e gradiente de `#8b5cf6` para `#10b981`.
- Crie uma animação `@keyframes float` (sobe e desce 20px) e a classe `.animate-float`.

**2. Navbar (Fixed):**
- Use Alpine.js (`x-data="{ scrolled: false }" @scroll.window="..."`) para que a nav fique transparente no topo, mas receba `.glass` ao rolar a página.
- Esquerda: Logo. Centro: Links. Direita: Botão "Entrar" (link para `{% url 'accounts:login' %}`) e "Começar grátis" (botão violeta apontando para `{% url 'accounts:register' %}`).

**3. Hero Section (Grid 2 colunas no Desktop):**
- **Background:** Adicione orbs brilhantes com `blur-3xl` nas cores violet e emerald.
- **Coluna Esquerda (Texto):** Badge animado, Título com `.gradient-text`, subtítulo, botões CTA (apontando para login/register) e Social Proof (avatares sobrepostos).
- **Coluna Direita (Mockup Desktop):** Card com `.glass` e `.animate-float`. Cabeçalho imitando botões macOS. Corpo exibindo "Saldo Total". **Inegociável:** Abaixo do saldo, dois cards: "**Entradas**" (verde) e "**Saídas**" (vermelho). *Nunca use receitas/despesas.*

**4. Secção de Features & CTA Final:**
- Grid de 3 colunas com cards `.glass` para os recursos.
- Secção CTA centralizada com botão redirecionando para o Cadastro. Footer simples na base.

**5. Telas de Autenticação (`accounts/login.html` e `accounts/register.html`):**
- Layout centralizado em tela cheia (`min-h-screen flex items-center justify-center relative`). Adicione os orbs brilhantes de fundo (`blur-3xl`) para manter a identidade.
- O formulário deve estar dentro de um container com a classe `.glass` (ex: `w-full max-w-md p-8 rounded-2xl glass`).
- **Inputs:** Fundo `bg-zinc-900/50`, borda `border-zinc-700`, foco `focus:ring-violet-500`. (Renderize os campos manualmente com o Tailwind).
- **Botões:** Largura total (`w-full`), fundo violeta ou gradiente.
- Inclua links no rodapé do form para alternar entre Login e Cadastro.

**Ação Final Obrigatória (@testes e @readme):**
Garanta que as rotas nos templates estão corretas e não geram erro 500. Crie testes simples (pytest) para garantir que as URLs `/`, `/accounts/login/` e `/accounts/register/` retornam status HTTP 200. Atualize o README documentando a implementação da Landing Page e do fluxo inicial de autenticação com o design Premium Dark.

## Fase 2: Modelagem, Admin Customizado e Motor de Auto-Categorização

**Contexto Inicial Obrigatório:** Antes de gerar qualquer código, leia e aplique rigorosamente as diretrizes contidas em `.github/copilot/instrucoes-gerais.md`. Lembre-se da nossa terminologia inegociável (Entradas/Saídas), do isolamento de regras de negócio no `services.py` e da proibição do uso do Admin nativo do Django.

**Objetivo:** Construir a camada de dados do app `finances` focada em integridade relacional, criar o alicerce do painel administrativo customizado e implementar o motor inteligente de importação e categorização de extratos bancários (CSV, OFX, PDF).

**Tarefas para o @backend:**
1. No app `finances`, desenvolva os modelos principais no `models.py`: 
   - `Category`: (nome, tipo [entrada/saída], fk para usuário, **keywords** [campo de texto para armazenar palavras-chave separadas por vírgula, essencial para a auto-categorização]).
   - `Transaction`: (valor, data, tipo [entrada/saída], descrição, fk para categoria, fk para usuário). 
   - Adicione validações a nível de banco (ex: valor > 0).
2. Para garantir o sucesso das fases futuras, crie o modelo `Account` (nome, tipo [conta_corrente/carteira/cartao_credito], fk para usuário). Relacione `Account` com `Transaction` (use `null=True, blank=True` temporariamente).
3. **Proibição:** NÃO registre nenhum modelo no arquivo `admin.py`.
4. **Novo App Admin:** Crie um novo app chamado `admin_panel`. Nele, crie CBVs básicas como `AdminDashboardView` e `AdminTransactionListView`. Proteja essas rotas usando `UserPassesTestMixin` garantindo que apenas `is_staff=True` tenham acesso.
5. **Motor de Importação (`services.py`):** Crie um serviço robusto chamado `process_bank_statement_import(file, user, account)`. 
   - O serviço deve conseguir ler CSV, OFX e PDF (adicione as bibliotecas necessárias como `ofxparse` ou `pdfplumber` no `requirements.txt`).
   - Para cada registro do extrato, o serviço deve fazer o rastreamento cruzando a descrição da transação com o campo `keywords` das Categorias daquele usuário.
   - Se encontrar uma palavra-chave correspondente, associa a categoria correta. Se não encontrar, deve associar a uma categoria genérica chamada "Avulsa" (criando-a automaticamente para o usuário caso não exista).
   - Salve as transações no banco garantindo o vínculo com o usuário e a conta informada.

**Tarefas para o @testes:**
1. Escreva testes unitários usando `pytest` focados na integridade dos modelos e métodos `__str__`.
2. Escreva testes de integração garantindo que um usuário comum recebe erro 403 ao tentar acessar o `admin_panel`.
3. **Testes do Motor de Importação:** Crie testes no `services.py` enviando listas de dicionários simulando as transações lidas de um arquivo. Valide se a auto-categorização funciona (ex: descrição "UBER TRIP" deve cair na categoria com keyword "uber", e "TARIFA BANCARIA" deve cair em "Avulsa" se não houver keyword correspondente).

**Ação Final Obrigatória (@readme):**
Gere as migrações. Execute todos os testes de banco de dados, permissão e do motor de importação. Atualize o `README.md` documentando o dicionário de dados gerado, a obrigatoriedade da FK de usuário e explique detalhadamente como funciona a inteligência do serviço de importação (quais formatos são aceitos e como a categoria "Avulsa" atua como fallback).

## Fase 3: Casos de Uso e Domínio (Services e Selectors)

**Contexto Inicial Obrigatório:** Revise os arquivos de contexto em `.github/instructions/django-project-standards.instructions.md`, `.github/skills/` e `.github/agents/` antes de prosseguir. O foco aqui é isolamento lógico.

**Objetivo:** Implementar as regras de negócio isoladas das views, fortalecendo a Arquitetura Limpa no app `finances`.

**Tarefas:**
1. No arquivo `services.py`, crie funções puramente focadas no negócio para: criar, editar e deletar transações. Faça tratamento de exceções adequado.
2. Crie uma função `calculate_balance` que processe e retorne o total de receitas, total de despesas e o saldo líquido.
3. No arquivo `selectors.py`, crie as funções de busca (ex: `get_all_transactions()`, `get_transaction_by_id()`), otimizando as queries com `select_related` ou `prefetch_related` quando necessário.
4. Escreva testes unitários rigorosos cobrindo os serviços e seletores, atestando que a lógica funciona de forma independente de qualquer requisição HTTP.

**Ação Final Obrigatória:** Execute a bateria de testes unitários. Atualize o `README.md` com a explicação de como o fluxo de dados funciona (View -> Service/Selector -> Model) e registre a conclusão da Fase 3.

## Fase 4: Interface Mobile-First, Views e Forms

**Contexto Inicial Obrigatório:** Consulte `.github/instructions/django-project-standards.instructions.md`, `.github/skills/` e `.github/agents/` para manter o padrão de código e UI estabelecidos.

**Objetivo:** Construir a interface de usuário focada em usabilidade mobile-first e conectar a lógica de domínio ao Django Templates.

**Tarefas:**
1. Crie os formulários baseados em modelos (`forms.py`) para `Transaction` e `Category`, incluindo classes CSS e validações amigáveis.
2. Desenvolva as views no app `finances` (Listar, Criar, Editar, Excluir). **Atenção:** as views devem ser enxutas. Elas extraem os dados do `request`, repassam para as funções do `services.py` e renderizam os templates com os dados do `selectors.py`.
3. Crie os templates HTML com foco total em mobile-first, garantindo tabelas/listas responsivas e botões acessíveis em telas de celular.
4. Crie testes de integração (Client test) verificando o fluxo de navegação e os status codes (200, 302).

**Ação Final Obrigatória:** Execute a suíte de testes de integração. Atualize o `README.md` descrevendo as decisões de design responsivo e detalhando as rotas (URLs) disponíveis até o momento.

## Fase 5: Dashboard e Diferenciais (Entrega Base)

**Contexto Inicial Obrigatório:** Leia as diretrizes em `.github/instructions/django-project-standards.instructions.md`, `.github/skills/` e `.github/agents/`. Esta fase consolida a entrega obrigatória e os diferenciais do hackathon.

**Objetivo:** Criar o painel gerencial e implementar filtros de pesquisa robustos.

**Tarefas:**
1. No app `dashboard`, crie a view principal que consome `calculate_balance` e renderiza um resumo financeiro limpo (Saldo Atual, Entradas, Saídas).
2. Volte ao `selectors.py` e adicione parâmetros opcionais de filtro (por período de datas, busca textual por descrição ou filtro por categoria).
3. Integre esses filtros na view de listagem de transações e crie a interface de busca no template HTML correspondente.
4. Adicione tratamento de erros visuais (messages framework do Django) para informar o usuário sobre ações bem-sucedidas ou erros de formulário.

**Ação Final Obrigatória:** Execute todos os testes do projeto. Revise o código para garantir que não há dados sensíveis expostos. Adicione um "Checklist de Entrega Base" ao `README.md` comprovando o cumprimento de todos os requisitos do regulamento. Fixe o passo a passo final para a banca avaliar o projeto.

## Fase 6: A Etapa Extra (Expansão do Sistema)

**Contexto Inicial Obrigatório:** Leia `.github/instructions/django-project-standards.instructions.md`, `.github/skills/` e `.github/agents/`. Aplique os conceitos de escalabilidade definidos lá.

**Objetivo:** Expandir a arquitetura implementando contas correntes, cartões e metas financeiras. *Esta é a feature surpresa para demonstrar controle automatizado.*

**Tarefas:**
1. Torne o relacionamento entre `Transaction` e `Account` obrigatório e funcional nos formulários e serviços.
2. Refatore os serviços (`services.py`) para exigir a conta/cartão de origem em cada movimentação. Envolva as operações de saldo em blocos `transaction.atomic()` para garantir segurança.
3. Atualize o template do Dashboard para separar e exibir o saldo por conta (ex: Carteira: R$50, Nubank: R$1000). O saldo de cartões deve refletir a fatura atual.
4. Crie o modelo `Goal` (Meta: nome, valor_alvo, valor_atual). Implemente a lógica no `services.py` e exiba uma barra de progresso visual (CSS) no Dashboard calculando a porcentagem de conclusão.

**Ação Final Obrigatória:** Escreva e execute os testes para as novas regras de múltiplas contas e metas. Atualize o `README.md` criando uma seção "Evolução do Sistema" para explicar à banca como a organização inicial da arquitetura permitiu essa expansão rápida com o auxílio da IA.

## Fase 7: Módulos de Conta Corrente e Cartão de Crédito

**Contexto Inicial Obrigatório:** Leia o arquivo `.github/copilot/instrucoes-gerais.md` antes de começar. Atue como Engenheiro Sênior especialista na stack do FinTrack (Django CBVs, Tailwind Dark-First, Services/Selectors). Use os agentes `@backend`, `@frontend` e `@testes` para dividir esta tarefa.

**Objetivo:** Implementar os módulos de Conta Corrente e Cartão de Crédito, integrando-os ao fluxo de Entradas e Saídas, com seus respectivos CRUDs e cálculos de saldo isolados.

**Tarefas para o @backend:**
1. No app `finances`, garanta que o modelo `Account` exista com os campos: `nome` e `tipo` (choices: 'conta_corrente', 'cartao_credito').
2. Garanta que o modelo `Transaction` tenha uma ForeignKey obrigatória para `Account`.
3. No arquivo `selectors.py`, crie uma função `get_account_balance(account_id)` que calcule o saldo específico daquela conta (Soma das Entradas - Soma das Saídas vinculadas a ela). Para o tipo 'cartao_credito', o foco deve ser a soma das Saídas (representando a fatura).
4. No arquivo `services.py`, atualize a lógica de criação e edição de transações para exigir e validar a conta informada.
5. Crie as CBVs (ListView, CreateView, UpdateView, DeleteView) separadas para gerenciar Contas Correntes e Cartões de Crédito. Lembre-se: `filter(user=request.user)` é inegociável.

**Tarefas para o @frontend:**
1. Atualize o formulário de "Adicionar Entrada/Saída" para incluir um `<select>` estilizado (Flowbite) listando as contas disponíveis do usuário.
2. Adicione opções claras no Menu de navegação para "Contas Correntes" e "Cartões".
3. Crie os templates de listagem (mobile-first, dark mode). Cada item da lista deve exibir o Nome da Conta e, ao lado, o seu Saldo atual (consumindo o seletor criado pelo backend). Use a cor verde (`text-green-400`) para saldos positivos em contas e vermelho (`text-red-400`) para a fatura dos cartões.
4. Adicione os botões de Editar e Excluir em cada item da lista.

**Ação Final Obrigatória (@testes e @readme):**
Escreva testes usando `pytest` para garantir que o saldo individual da Conta Corrente bate com as Entradas/Saídas vinculadas a ela, e que o relacionamento está obrigatório. Atualize o `README.md` da JRD Labs destacando a conclusão deste módulo robusto e como a Arquitetura Limpa suportou essa evolução.
