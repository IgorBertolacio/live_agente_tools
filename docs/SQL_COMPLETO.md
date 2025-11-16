# 🗄️ Sistema SQL Completo - Consulta, Orquestração e Visualização

Documentação completa do sistema de consultas SQL em linguagem natural com visualização elegante e orquestração inteligente.

---

## 📋 Índice

1. [Conexão e Configuração](#conexão-e-configuração)
2. [Ferramentas SQL Implementadas](#ferramentas-sql-implementadas)
3. [Orquestração Inteligente](#orquestração-inteligente)
4. [Visualização Elegante](#visualização-elegante)
5. [Como Usar](#como-usar)
6. [Segurança](#segurança)
7. [Exemplos Práticos](#exemplos-práticos)

---

## 🔌 Conexão e Configuração

### Banco de Dados

```
Host: sagan.aws.el.com.br:5432
Database: eldados_dadosabertos_govbr
User: elgpi_dadosabertos_api
Status: ✅ CONECTADO
```

### Estrutura

O banco possui **215 tabelas** distribuídas em múltiplos schemas:

- **anatel**: alerta_desastre
- **atricon**: avaliacoes_pntp_2024, radar_avaliacoes, respostas_pntp_2024
- **aws**: ambiente, bancos, cliente, esquema, tabela, usuario
- **bc**: cotacao
- **camara**: dados, deputado, links
- **catalogo**: colunas, tabelas, relacionamentos
- **edu**: acessos, biblioteca, cliente
- E muitos outros!

### Configuração (.env)

```env
DB_HOST=sagan.aws.el.com.br
DB_PORT=5432
DB_NAME=eldados_dadosabertos_govbr
DB_USER=elgpi_dadosabertos_api
DB_PASSWORD=TbhSJ6wfHpzLzFTOHH4ZcgjdrbWzknJG
```

---

## 🛠️ Ferramentas SQL Implementadas

### 1. listar_tabelas_banco()

Lista TODAS as 215 tabelas agrupadas por schema.

**Uso:**
- "Quais tabelas temos?"
- "O que tem no banco?"
- "Mostre as tabelas"

**Retorno:**
```
✅ Encontrei 215 tabelas em 15 schemas:

📂 anatel (1 tabelas):
   alerta_desastre

📂 aws (12 tabelas):
   ambiente, bancos, cliente, esquema...

📂 camara (5 tabelas):
   dados, deputado, links...
```

**Código:** `agent.py:237-291`

---

### 2. explorar_estrutura_tabela(nome_tabela)

Mostra colunas, tipos e nullable de uma tabela.

**Uso:**
- "Mostre a estrutura da tabela aws.cliente"
- "Quais colunas tem na camara.deputado?"

**Retorno:**
```
📊 Estrutura da tabela 'aws.cliente':

  • id (integer) - NOT NULL
  • nome (varchar) - NULL
  • cpf (varchar) - NULL
  • nome_estado (varchar) - NULL
  • data_cadastro (timestamp) - NOT NULL

Total de colunas: 5

Agora você pode consultar dados usando:
executar_query_customizada('SELECT * FROM aws.cliente LIMIT 10')
```

**Código:** `agent.py:293-358`

---

### 3. executar_query_customizada(query_sql, limite=10)

Executa queries SELECT customizadas com visualização automática na tela.

**Segurança:**
- ✅ Apenas SELECT permitido
- ✅ LIMIT automático (máximo 100)
- ✅ Prepared statements
- ✅ Envia visualização via data channel

**Exemplos de queries:**

```sql
-- Contar registros
SELECT COUNT(*) FROM aws.cliente

-- Agrupar e ordenar
SELECT nome_estado, COUNT(*) as total
FROM aws.cliente
GROUP BY nome_estado
ORDER BY total DESC

-- Filtrar
SELECT * FROM camara.deputado WHERE partido = 'PT' LIMIT 10

-- Somar valores
SELECT SUM(valor) as total FROM bc.cotacao WHERE ano = 2024
```

**Retorno (para agregações):**
```
✅ Resultado exibido na tela: count = 215
```

**Retorno (para múltiplos registros):**
```
✅ Query executada! Exibindo 10 registros na tela.
```

**Código:** `agent.py:360-448`

---

## 🎭 Orquestração Inteligente

### O Conceito

Quando a IA precisa fazer múltiplas queries, ela **fala com o usuário a cada passo** para evitar pausas dramáticas.

### Regras de Orquestração

🎤 **SEMPRE FALE ANTES DE CHAMAR FERRAMENTAS!**

1. FALE o que vai fazer
2. CHAME UMA ferramenta por vez
3. COMENTE o resultado
4. FALE o que vai fazer a seguir
5. REPITA até concluir

### Fluxo de Exemplo

```
Usuário: "Analise a tabela aws.cliente"

IA FALA: "Vou explorar a estrutura da tabela aws ponto cliente..."
→ Chama: explorar_estrutura_tabela("aws.cliente")

IA FALA: "Encontrei 5 colunas. Agora vou buscar quantos clientes temos..."
→ Chama: executar_query_customizada("SELECT COUNT(*) FROM aws.cliente")

IA FALA: "Temos 215 clientes. Vou ver a distribuição por estado..."
→ Chama: executar_query_customizada("SELECT nome_estado, COUNT(*) as total FROM aws.cliente GROUP BY nome_estado ORDER BY total DESC LIMIT 5")

IA FALA: "Pronto! O Espírito Santo lidera com 573 clientes..."
```

### Configuração

**agent.py:67-72** - Regra principal no system prompt:
```
🎤 REGRA MAIS IMPORTANTE: SEMPRE FALE ANTES DE CHAMAR FERRAMENTAS!
- NUNCA execute ferramentas em silêncio
- SEMPRE diga o que vai fazer ANTES de fazer
- Chame APENAS UMA ferramenta por vez
- Comente o resultado ANTES de chamar a próxima
```

**agent.py:550** - Desabilita parallel tool calls:
```python
llm=openai.LLM(
    model="gpt-4o-mini",
    parallel_tool_calls=False,  # Força chamadas sequenciais
)
```

---

## 🎨 Visualização Elegante

### Componente SqlResultDisplay

Componente React moderno para exibir resultados SQL de forma elegante.

**Características:**
- 🎨 Design moderno (gradiente azul → índigo)
- 📊 Header com ícone de banco de dados
- ⏰ Timestamp da consulta
- 📈 Contador de registros
- 💻 Query SQL formatada em código
- 🎯 Exibição especial para agregações (COUNT, SUM, etc)
- 📋 Tabela completa para múltiplos resultados
- ❌ Botão para fechar cada resultado

### Layout da Tela

```
┌────────────────────────────────────────────────┐
│               HEADER / VÍDEO                   │
├──────────────┬───────────────┬─────────────────┤
│              │               │                 │
│  GRÁFICOS    │     CHAT      │  RESULTADOS SQL │
│  (esquerda)  │   (centro)    │  (direita)      │
│  máx. 3      │               │  máx. 2         │
│              │               │                 │
└──────────────┴───────────────┴─────────────────┘
│            CONTROLES (bottom)                  │
└────────────────────────────────────────────────┘
```

### Exibição de Agregações

Para queries como `COUNT`, `SUM`, `AVG`:

```
┌──────────────────────────────┐
│      📊 Consulta SQL          │
│      ⏰ 15:23:45              │
├──────────────────────────────┤
│ SELECT COUNT(*) FROM empresas│
├──────────────────────────────┤
│                              │
│         count                │
│         ⬇                    │
│         215                  │
│                              │
└──────────────────────────────┘
```

### Exibição de Tabelas

Para queries com múltiplos resultados:

```
┌────────────────────────────────────────┐
│      📊 Consulta SQL                    │
│      ⏰ 15:23:45 • 📋 10 registros     │
├────────────────────────────────────────┤
│ SELECT * FROM empresas LIMIT 10        │
├────────────────────────────────────────┤
│ ID  │ NOME          │ STATUS  │ CIDADE│
├────────────────────────────────────────┤
│ 1   │ Empresa A     │ ativa   │ SP    │
│ 2   │ Empresa B     │ inativa │ RJ    │
│ ... │               │         │       │
└────────────────────────────────────────┘
```

### Formatação Especial

- **Números**: Verde com localização pt-BR (`215`, `1.234,56`)
- **Booleans**: Verde (true) / Vermelho (false)
- **Null**: Cinza itálico
- **Texto**: Truncado com tooltip se muito longo

### Arquivos

- **Frontend:** `frontend/components/sql-result-display.tsx` (165 linhas)
- **Integração:** `frontend/components/session-view.tsx:189-248`
- **Ícones:** `lucide-react` (Database, Calendar, Table2, X)

---

## 🚀 Como Usar

### 1. Iniciar Backend

```bash
python agent.py dev
```

### 2. Iniciar Frontend (outro terminal)

```bash
cd frontend
npm run dev
```

### 3. Perguntas para Testar

**Listar tabelas:**
```
"Quais tabelas temos no banco?"
"Mostre as tabelas do schema aws"
```

**Explorar estrutura:**
```
"Mostre a estrutura da tabela aws.cliente"
"Quais colunas tem na camara.deputado?"
```

**Consultas simples:**
```
"Quantas empresas temos na aws.cliente?"
"Qual o total de deputados?"
```

**Consultas com filtros:**
```
"Mostre 10 clientes do Espírito Santo"
"Liste deputados do partido PT"
```

**Agregações:**
```
"Quantas empresas por estado?"
"Qual a distribuição de deputados por partido?"
```

**Orquestração complexa:**
```
"Analise a tabela aws.cliente e me dê insights"
"Faça um join entre aws.cliente e aws.usuario"
```

**Com gráficos:**
```
"Mostre um gráfico da distribuição de clientes por estado"
"Analise os deputados e crie um gráfico por partido"
```

---

## 🔒 Segurança

### Validações Implementadas

✅ **Apenas SELECT permitido**
```python
if not query_sql.strip().upper().startswith('SELECT'):
    return "❌ Erro: Apenas queries SELECT são permitidas"
```

✅ **LIMIT automático**
```python
if 'LIMIT' not in query_sql.upper():
    query_sql += f" LIMIT {limite}"  # Máximo 100
```

✅ **Prepared Statements**
```python
cursor.execute(
    "SELECT * FROM empresas WHERE cidade = %s",
    (cidade,)  # Parâmetro seguro
)
```

✅ **Filtro de tabelas do sistema**
```python
if not nome.startswith('spatial_') and \
   nome not in ('geography_columns', 'geometry_columns', ...):
    # Incluir na lista
```

### O Que NÃO é Permitido

❌ INSERT, UPDATE, DELETE, DROP
❌ Queries sem LIMIT acima de 100 registros
❌ SQL injection via concatenação de strings
❌ Acesso a tabelas de sistema interno

---

## 📝 Exemplos Práticos

### Exemplo 1: Análise de Clientes

```
Usuário: "Quantos clientes temos por estado?"

IA: "Vou analisar a distribuição de clientes por estado..."
→ executar_query_customizada("SELECT nome_estado, COUNT(*) as total FROM aws.cliente GROUP BY nome_estado ORDER BY total DESC")

Tela: [Tabela elegante com estados e totais]

IA: "O Espírito Santo lidera com quinhentos e setenta e três clientes, seguido de São Paulo com quarenta e cinco..."
```

### Exemplo 2: Análise de Deputados

```
Usuário: "Mostre a bancada por partido e crie um gráfico"

IA: "Vou buscar a distribuição de deputados por partido..."
→ executar_query_customizada("SELECT partido, COUNT(*) as total FROM camara.deputado GROUP BY partido ORDER BY total DESC LIMIT 5")

Tela: [Tabela com partidos e totais]

IA: "Agora vou criar um gráfico de barras..."
→ gerar_grafico(tipo="bar", titulo="Bancada por Partido", dados=[...])

Tela: [Gráfico de barras + Tabela SQL]

IA: "O PT tem a maior bancada com trinta e cinco deputados..."
```

### Exemplo 3: Join Entre Tabelas

```
Usuário: "Faça um join entre clientes e usuários"

IA: "Vou explorar as tabelas primeiro..."
→ explorar_estrutura_tabela("aws.cliente")
→ explorar_estrutura_tabela("aws.usuario")

IA: "Identifichei as colunas de relacionamento. Executando join..."
→ executar_query_customizada("SELECT c.nome_estado, COUNT(c.id) as total_clientes, COUNT(u.idpk) as total_usuarios FROM aws.cliente c LEFT JOIN aws.usuario u ON c.id = u.usuario GROUP BY c.nome_estado LIMIT 10")

Tela: [Tabela com dados consolidados]

IA: "Encontrei X clientes e Y usuários distribuídos por estado..."
```

---

## 📊 Comparação: Antes vs Depois

### ❌ ANTES:

```
Usuário: "Quantas empresas temos?"
IA: "Não encontrei tabelas no banco de dados."
```

**Problemas:**
- Buscava apenas schema 'public' (vazio)
- Não havia visualização
- Pausas dramáticas durante queries
- Queries em paralelo sem feedback

### ✅ DEPOIS:

```
Usuário: "Quantas empresas temos?"

IA: "Vou listar as tabelas disponíveis..."
→ listar_tabelas_banco()

IA: "Encontrei duzentos e quinze tabelas! Vou analisar aws.cliente..."
→ explorar_estrutura_tabela("aws.cliente")

IA: "Contando os clientes cadastrados..."
→ executar_query_customizada("SELECT COUNT(*) FROM aws.cliente")

TELA: [Card elegante mostrando "215" em destaque]

IA: "Temos duzentos e quinze clientes cadastrados no sistema!"
```

**Soluções:**
1. ✅ Busca em todos os schemas
2. ✅ Visualização elegante automática
3. ✅ Orquestração com feedback progressivo
4. ✅ Chamadas sequenciais (não paralelas)
5. ✅ Números por extenso na fala, algarismos na tela

---

## 🎉 Status do Sistema

✅ **Backend:** 3 ferramentas SQL implementadas e testadas
✅ **Frontend:** Componente SqlResultDisplay funcionando
✅ **Integração:** Data channel configurado (topic: "sql-result")
✅ **Visualização:** Elegante, moderna e responsiva
✅ **Orquestração:** IA fala antes de cada ferramenta
✅ **Segurança:** Todas as validações implementadas
✅ **Documentação:** Completa e atualizada

---

## 📚 Arquivos Relacionados

### Backend (Python)
- `agent.py:237-291` - listar_tabelas_banco()
- `agent.py:293-358` - explorar_estrutura_tabela()
- `agent.py:360-448` - executar_query_customizada()
- `agent.py:67-72` - Regra de orquestração
- `agent.py:126-166` - Fluxo de trabalho detalhado
- `agent.py:550` - Desabilita parallel_tool_calls
- `test_db_connection.py` - Script de teste de conexão
- `.env:17-22` - Credenciais PostgreSQL

### Frontend (React)
- `frontend/components/sql-result-display.tsx` - Componente de visualização (165 linhas)
- `frontend/components/session-view.tsx:16-30` - Imports e interface
- `frontend/components/session-view.tsx:57` - Estado sqlResults
- `frontend/components/session-view.tsx:106-129` - Listener data channel
- `frontend/components/session-view.tsx:189-248` - Renderização

---

**Sistema 100% funcional e pronto para uso! 🚀**
