# FinTrack - JRD Labs

Aplicacao Django para controle de Entradas e Saidas com Arquitetura Limpa, Dashboard HTMX + ApexCharts, autenticacao e modulo de contas/cartoes.

## Stack

- Python 3.13
- Django 5.2
- HTMX
- ApexCharts (CDN)
- Tailwind CSS (CDN)
- Alpine.js (CDN)
- Pytest + pytest-django
- ofxparse + pdfplumber

## Como executar

1. Criar/ativar ambiente virtual (opcional, se ainda nao existir):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. Aplicar migracoes:

```powershell
python manage.py migrate
```

4. Executar servidor:

```powershell
python manage.py runserver
```

5. Executar testes:

```powershell
pytest -q
```

## Arquitetura Limpa adotada

Separacao principal por app:

- `core`: landing page e configuracoes iniciais
- `accounts`: login, logout e registro
- `finances`: dominio financeiro (modelos, regras e consultas)
- `dashboard`: camada de apresentacao e graficos HTMX/Apex
- `admin_panel`: painel administrativo customizado (sem Django admin nativo para modelos de negocio)

Fluxo de dados:

`View -> Service/Selector -> Model`

Regras:

- `services.py`: comandos e regra de negocio (CUD e importacao)
- `selectors.py`: consultas e agregacoes (Read)
- `views.py`: enxutas, apenas orquestram request/response
- Nenhuma query complexa em view

## Dicionario de dados

### Category
- `user` (FK obrigatoria)
- `nome`
- `tipo` (`entrada` ou `saida`)
- `keywords` (texto com palavras-chave separadas por virgula)

### Account
- `user` (FK obrigatoria)
- `nome`
- `tipo` (`conta_corrente`, `carteira`, `cartao_credito`)

### Transaction
- `user` (FK obrigatoria)
- `account` (FK obrigatoria)
- `category` (FK opcional)
- `valor` (validacao `> 0`)
- `data`
- `tipo` (`entrada` ou `saida`)
- `descricao`

### Goal
- `user` (FK obrigatoria)
- `nome`
- `valor_alvo`
- `valor_atual`
- `percentual_conclusao` (propriedade)

## Dashboard com HTMX (Lazy Loading)

Na tela principal (`/dashboard/`), cada card de grafico carrega de forma assincroma:

- `hx-get` para rotas especificas
- `hx-trigger="load"` para disparo automatico ao abrir a pagina
- cada rota retorna fragmento HTML com script ApexCharts

Rotas HTMX:

- `/dashboard/grafico-evolucao/`
- `/dashboard/grafico-saidas/`
- `/dashboard/grafico-metas/`
- `/dashboard/grafico-investimentos/`

Configuracao visual dos graficos:

- tema dark
- background transparente
- grafico de evolucao em area smooth com gradiente
- Entradas em verde (`#4ADE80`)
- Saidas em vermelho (`#F87171`)
- donuts sem borda para distribuicao

## Landing page e autenticacao (Premium Dark)

Implementacoes:

- Landing em `/`
- Landing redireciona para dashboard quando usuario ja esta logado
- Login em `/accounts/login/`
- Cadastro em `/accounts/register/`
- Login redireciona para `/dashboard/` quando autenticacao e bem-sucedida
- Usuario ja autenticado e redirecionado para dashboard ao acessar login/cadastro
- Navbar com comportamento via Alpine (`glass` ao scroll)
- Hero com identidade visual dark, orbs com blur e card flutuante
- Terminologia mantida: Entradas e Saidas

Perfil e preferencias:

- Rota `/accounts/profile/` para ajustar moeda e formato de data
- Preferencias criadas automaticamente no cadastro
- Dashboard e listagens aplicam moeda e data conforme preferencia do usuario

## Motor de importacao de extratos

Servico: `finances.services.process_bank_statement_import(file, user, account)`

Fluxo pela interface:

- Rota `/finances/transactions/import/`
- Formulario com selecao de conta + upload de arquivo
- Integrado ao mesmo service de importacao e mensagens visuais de sucesso/erro

Formatos suportados:

- CSV
- OFX
- PDF (parser baseline por linha delimitada por `;`)

Inteligencia de categorizacao:

1. Le as transacoes
2. Normaliza descricao/tipo/valor/data
3. Cruza descricao com `keywords` das categorias do usuario
4. Quando encontrar match, associa categoria correspondente
5. Quando nao encontrar, usa categoria fallback `Avulsa` (auto-criada por usuario/tipo)
6. Persiste transacoes com vinculo de usuario e conta

Validacoes robustas:

- CSV com validacao de colunas obrigatorias
- Validacao amigavel por linha (data, valor, tipo e descricao)
- Erros descritivos com referencia da linha invalida

## Modulo Conta Corrente e Cartao

Implementado:

- FK obrigatoria de `Transaction` para `Account`
- Seletor `get_account_balance(account_id)`
- Saldo por conta corrente: Entradas - Saidas
- Fatura de cartao: soma das Saidas
- CRUD separado por tipo (CBVs distintas para conta corrente e cartao):
  - `/finances/accounts/contas-correntes/`
  - `/finances/accounts/contas-correntes/new/`
  - `/finances/accounts/contas-correntes/<id>/edit/`
  - `/finances/accounts/contas-correntes/<id>/delete/`
  - `/finances/accounts/cartoes/`
  - `/finances/accounts/cartoes/new/`
  - `/finances/accounts/cartoes/<id>/edit/`
  - `/finances/accounts/cartoes/<id>/delete/`
- Formulario de transacao com selecao de conta
- Dashboard com barra de progresso visual para metas financeiras

## Rotas principais

- `/` landing
- `/accounts/login/`
- `/accounts/register/`
- `/accounts/profile/`
- `/dashboard/`
- `/finances/transactions/`
- `/finances/transactions/import/`
- `/finances/categories/`
- `/finances/categories/new/`
- `/finances/categories/<id>/edit/`
- `/finances/categories/<id>/delete/`
- `/finances/goals/`
- `/finances/goals/new/`
- `/finances/goals/<id>/edit/`
- `/finances/goals/<id>/delete/`
- `/finances/accounts/contas-correntes/`
- `/finances/accounts/cartoes/`
- `/admin-panel/` (apenas `is_staff=True`)

## Navegacao autenticada

- Menu global unificado disponivel em todas as paginas protegidas
- Sidebar fixa no desktop e drawer no mobile
- Sidebar com estado ativo por rota e design premium dark atualizado
- Itens da navegacao com icones SVG e feedback visual consistente (hover/focus)
- Links para Dashboard, Transacoes, Importar, Categorias, Metas, Contas, Cartoes e Perfil
- Acao de logout pelo proprio menu
- Breadcrumb dinamico nas telas internas para orientacao de contexto

## Frontend interno

- Padrão visual das telas internas alinhado ao estilo da landing (glass, gradientes e hierarchy tipografica)
- Formularios internos com estrutura consistente, feedback de erro e acoes claras (Cancelar/Salvar)
- Shell autenticado com atmosfera visual (orbs e profundidade) mantendo performance
- Microanimacoes de entrada (cards, listas e formularios) com transicoes suaves
- Dashboard refinado para mobile (densidade, contraste e legibilidade)

## Acessibilidade e usabilidade

- Foco visivel padronizado para links, botoes e campos (teclado)
- Estados `hover`, `focus-visible` e `transition` consistentes nas principais interacoes
- Suporte a `prefers-reduced-motion` para reduzir animacoes quando solicitado pelo usuario
- Contraste de textos secundarios reforcado em dashboard, breadcrumb e listagens
- Login e cadastro com `label` associado (`for/id`) e `autocomplete` apropriado

## Testes implementados

- URLs publicas (`/`, login, registro) com status 200
- Rotas HTMX do dashboard com status 200
- Restricao do admin panel para usuario comum (403)
- Integridade basica de modelos e `__str__`
- Obrigatoriedade de conta na criacao de transacao
- Calculo de saldo por conta/cartao
- Auto-categorizacao e fallback Avulsa no importador
- CRUD de metas e atualizacao de progresso
- CRUD de categorias e filtro por categoria na listagem de transacoes
- Paginacao das listagens principais
- Fluxo de perfil/preferencias do usuario
- Mensagens de erro amigaveis no importador
- Redirecionamento de login e protecao de rotas autenticadas
- Formatação de moeda/data por preferencias em templates
- Importacao de extrato end-to-end pela interface
- Cobertura de autorizacao para rotas protegidas (dashboard, financas e perfil)
- Validacao de acesso admin customizado: staff 200, nao staff 403
- Landing autenticada redirecionando para dashboard
- Menu global presente nas paginas protegidas
- Ajustes de contraste e foco nas listagens de transacoes, contas, categorias e metas

Execucao atual:

- `44 passed` (ultimo ciclo validado)

## Checklist de Entrega Base

- [x] Projeto Django inicializado sem DRF e sem Docker
- [x] Apps `core`, `accounts`, `finances`, `dashboard`, `admin_panel`
- [x] Arquitetura com `services.py` e `selectors.py`
- [x] Dashboard com HTMX lazy loading e ApexCharts dark
- [x] Landing page + fluxo inicial de autenticacao
- [x] Modelagem financeira com FK obrigatoria de usuario
- [x] Motor de importacao e categorizacao com fallback Avulsa
- [x] Modulo de contas correntes e cartoes
- [x] Modulo de metas com CRUD e barra de progresso
- [x] Paginacao e UX mobile refinada em listagens
- [x] Importador robusto com validacoes amigaveis
- [x] Perfil com preferencias de moeda e data
- [x] Navegacao interna com icones, breadcrumb dinamico e microanimacoes
- [x] Passe de acessibilidade (foco visivel, reduced motion e contraste)
- [x] Testes automatizados com pytest

## Evolucao do sistema

A separacao entre views enxutas, services (regras) e selectors (consultas) permitiu adicionar conta/cartao, dashboard e importador sem acoplamento excessivo. Essa base foi preparada para ampliar metas, filtros avancados e novos modulos mantendo organizacao e qualidade de testes.
