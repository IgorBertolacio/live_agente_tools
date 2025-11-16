# 🛠️ Exemplos de Ferramentas Customizadas

## ✅ SIM, você pode criar QUALQUER ferramenta!

LiveKit Function Tools permite integrar com:
- 🗄️ Bancos de dados (SQL, NoSQL)
- 🌐 APIs externas (REST, GraphQL)
- 📁 Arquivos locais
- 🔍 Sistemas de busca
- 📧 Serviços de email
- E muito mais!

---

## 📚 Exemplos Práticos

### 1. Consulta a Banco SQL (PostgreSQL)

```python
import psycopg2
from livekit.agents import function_tool, RunContext
from typing import Annotated

@function_tool()
async def consultar_funcionarios(
    self,
    ctx: RunContext,
    cargo: Annotated[str, "Cargo a filtrar (ex: 'professor', 'médico')"],
) -> str:
    """Busca funcionários por cargo no banco de dados."""
    try:
        # Conectar ao PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            database="prefeitura",
            user="admin",
            password="senha123"
        )
        cursor = conn.cursor()

        # Executar query
        cursor.execute(
            "SELECT nome, cargo, salario FROM funcionarios WHERE cargo = %s",
            (cargo,)
        )
        resultados = cursor.fetchall()

        # Fechar conexão
        cursor.close()
        conn.close()

        # Formatar resposta
        if resultados:
            funcionarios = [
                f"{nome} - {cargo} - R$ {salario:.2f}"
                for nome, cargo, salario in resultados
            ]
            return f"Encontrados {len(resultados)} funcionários:\n" + "\n".join(funcionarios)
        else:
            return f"Nenhum funcionário encontrado com cargo '{cargo}'"

    except Exception as e:
        return f"Erro ao consultar banco: {str(e)}"
```

### 2. Consulta a MongoDB

```python
from pymongo import MongoClient
from livekit.agents import function_tool, RunContext
from typing import Annotated

@function_tool()
async def buscar_empresa_mongo(
    self,
    ctx: RunContext,
    cnpj: Annotated[str, "CNPJ da empresa"],
) -> str:
    """Busca empresa no MongoDB."""
    try:
        # Conectar ao MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['prefeitura']
        collection = db['empresas']

        # Buscar empresa
        empresa = collection.find_one({"cnpj": cnpj})

        client.close()

        if empresa:
            return f"""Empresa encontrada:
Nome: {empresa.get('nome')}
CNPJ: {empresa.get('cnpj')}
Status: {empresa.get('status')}
Regime: {empresa.get('regime')}"""
        else:
            return f"Empresa com CNPJ {cnpj} não encontrada"

    except Exception as e:
        return f"Erro: {str(e)}"
```

### 3. API Externa (HTTP Request)

```python
import requests
from livekit.agents import function_tool, RunContext
from typing import Annotated

@function_tool()
async def consultar_cep(
    self,
    ctx: RunContext,
    cep: Annotated[str, "CEP a consultar (apenas números)"],
) -> str:
    """Consulta informações de endereço via API ViaCEP."""
    try:
        # Fazer requisição HTTP
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        response.raise_for_status()

        data = response.json()

        if "erro" in data:
            return f"CEP {cep} não encontrado"

        return f"""Endereço:
Logradouro: {data.get('logradouro')}
Bairro: {data.get('bairro')}
Cidade: {data.get('localidade')}
Estado: {data.get('uf')}"""

    except Exception as e:
        return f"Erro ao consultar CEP: {str(e)}"
```

### 4. Busca em Elasticsearch

```python
from elasticsearch import Elasticsearch
from livekit.agents import function_tool, RunContext
from typing import Annotated

@function_tool()
async def buscar_documentos(
    self,
    ctx: RunContext,
    termo: Annotated[str, "Termo de busca"],
) -> str:
    """Busca documentos no Elasticsearch."""
    try:
        # Conectar ao Elasticsearch
        es = Elasticsearch(['http://localhost:9200'])

        # Fazer busca
        resultado = es.search(
            index="documentos",
            body={
                "query": {
                    "match": {
                        "conteudo": termo
                    }
                }
            }
        )

        hits = resultado['hits']['hits']

        if hits:
            docs = [
                f"{hit['_source']['titulo']} (Score: {hit['_score']:.2f})"
                for hit in hits[:5]  # Top 5 resultados
            ]
            return f"Encontrados {len(hits)} documentos:\n" + "\n".join(docs)
        else:
            return f"Nenhum documento encontrado para '{termo}'"

    except Exception as e:
        return f"Erro: {str(e)}"
```

### 5. Ler Arquivos CSV

```python
import csv
from livekit.agents import function_tool, RunContext
from typing import Annotated

@function_tool()
async def consultar_csv(
    self,
    ctx: RunContext,
    arquivo: Annotated[str, "Nome do arquivo CSV"],
    coluna: Annotated[str, "Coluna a buscar"],
) -> str:
    """Lê dados de arquivo CSV."""
    try:
        with open(f"data/{arquivo}.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            dados = list(reader)

        if coluna in dados[0]:
            valores = [row[coluna] for row in dados]
            return f"Valores encontrados em '{coluna}':\n" + "\n".join(valores[:10])
        else:
            return f"Coluna '{coluna}' não encontrada"

    except FileNotFoundError:
        return f"Arquivo '{arquivo}.csv' não encontrado"
    except Exception as e:
        return f"Erro: {str(e)}"
```

### 6. Enviar Email

```python
import smtplib
from email.mime.text import MIMEText
from livekit.agents import function_tool, RunContext
from typing import Annotated

@function_tool()
async def enviar_email(
    self,
    ctx: RunContext,
    destinatario: Annotated[str, "Email do destinatário"],
    assunto: Annotated[str, "Assunto do email"],
    mensagem: Annotated[str, "Conteúdo do email"],
) -> str:
    """Envia email via SMTP."""
    try:
        msg = MIMEText(mensagem)
        msg['Subject'] = assunto
        msg['From'] = 'noreply@prefeitura.gov.br'
        msg['To'] = destinatario

        # Conectar ao servidor SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('user@gmail.com', 'senha')
            server.send_message(msg)

        return f"Email enviado com sucesso para {destinatario}"

    except Exception as e:
        return f"Erro ao enviar email: {str(e)}"
```

### 7. Processar Pagamento (API Stripe)

```python
import stripe
from livekit.agents import function_tool, RunContext
from typing import Annotated

stripe.api_key = "sk_test_..."

@function_tool()
async def processar_pagamento(
    self,
    ctx: RunContext,
    valor: Annotated[float, "Valor em reais"],
    descricao: Annotated[str, "Descrição do pagamento"],
) -> str:
    """Cria uma intenção de pagamento via Stripe."""
    try:
        # Criar payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(valor * 100),  # Centavos
            currency="brl",
            description=descricao,
        )

        return f"Pagamento criado! ID: {intent.id}"

    except Exception as e:
        return f"Erro: {str(e)}"
```

### 8. Executar Cálculos Complexos

```python
import numpy as np
from livekit.agents import function_tool, RunContext
from typing import Annotated

@function_tool()
async def calcular_estatisticas(
    self,
    ctx: RunContext,
    valores: Annotated[str, "Lista de valores separados por vírgula"],
) -> str:
    """Calcula estatísticas de uma série de valores."""
    try:
        # Converter string em array
        numeros = [float(x.strip()) for x in valores.split(',')]
        arr = np.array(numeros)

        # Calcular estatísticas
        estatisticas = {
            "média": float(np.mean(arr)),
            "mediana": float(np.median(arr)),
            "desvio_padrão": float(np.std(arr)),
            "mínimo": float(np.min(arr)),
            "máximo": float(np.max(arr)),
        }

        return f"Estatísticas calculadas:\n{json.dumps(estatisticas, indent=2)}"

    except Exception as e:
        return f"Erro: {str(e)}"
```

---

## 🚀 Como Adicionar ao Seu Agente

1. **Adicione o decorator** `@function_tool()` acima da função
2. **Coloque dentro da classe** `ElVideoBotAgent`
3. **Use type hints** com `Annotated` para documentar
4. **Retorne string** com o resultado

```python
class ElVideoBotAgent(Agent):
    @function_tool()
    async def sua_ferramenta(
        self,
        ctx: RunContext,
        parametro: Annotated[str, "Descrição do parâmetro"],
    ) -> str:
        # Sua lógica aqui
        return "Resultado"
```

---

## 💡 Dicas Importantes

### ✅ Boas Práticas

1. **Sempre use try/except** para tratar erros
2. **Retorne mensagens claras** para a IA
3. **Use type hints** para documentação
4. **Feche conexões** (databases, arquivos)
5. **Use async** quando possível

### ⚠️ Cuidados

1. **Senhas**: Use variáveis de ambiente, nunca hardcode
2. **Timeout**: APIs externas podem demorar
3. **Rate limiting**: Respeite limites de APIs
4. **Validação**: Valide inputs do usuário
5. **Segurança**: Sanitize queries SQL (use prepared statements)

### 🔒 Segurança

```python
# ❌ NUNCA FAÇA ISSO (SQL Injection)
cursor.execute(f"SELECT * FROM users WHERE name = '{nome}'")

# ✅ SEMPRE FAÇA ISSO
cursor.execute("SELECT * FROM users WHERE name = %s", (nome,))
```

---

## 📝 Testando

Depois de adicionar a ferramenta:

```bash
python agent.py dev
```

**Fale com a IA:**
- "Consulte quantos funcionários ativos temos"
- "Busque a empresa com CNPJ 12345678000100"
- "Qual o endereço do CEP 01310100?"

A IA vai **automaticamente chamar** a ferramenta apropriada! 🎉

---

## 🎯 Exemplos Reais de Uso

### Prefeitura Digital

```python
@function_tool()
async def consultar_protocolo(self, ctx, numero_protocolo):
    # Buscar protocolo no banco
    # Retornar status e informações
    pass

@function_tool()
async def agendar_atendimento(self, ctx, cpf, servico, data):
    # Criar agendamento
    # Enviar confirmação por email
    pass
```

### E-commerce

```python
@function_tool()
async def consultar_estoque(self, ctx, produto_id):
    # Verificar estoque
    pass

@function_tool()
async def criar_pedido(self, ctx, itens, cpf):
    # Processar pedido
    pass
```

---

**Agora você pode criar QUALQUER integração!** 🚀
