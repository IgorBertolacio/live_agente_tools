"""
El Video Bot - Agente de vídeo com avatar ANAM
Recebe áudio em português, transcreve, analisa com GPT-4o-mini,
gera resposta em texto, converte para vídeo com ANAM e áudio com ElevenLabs
"""

import logging
import os
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobRequest,
    WorkerOptions,
    WorkerType,
    RoomInputOptions,
    cli,
    function_tool,
    RunContext,
    get_job_context,
)
from livekit.plugins import openai, elevenlabs, silero  # , anam  # DESABILITADO PROVISORIAMENTE
import json
from typing import Annotated, Any
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger("el-video-bot")
logger.setLevel(logging.INFO)

load_dotenv()

AGENT_NAME = "El Video Bot"

# Carregar base de conhecimento
def load_knowledge_base():
    """Carrega a base de conhecimento do arquivo"""
    try:
        with open("knowledge_base.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning("Arquivo knowledge_base.txt não encontrado")
        return ""

KNOWLEDGE_BASE = load_knowledge_base()


# Configuração do banco de dados
def get_db_connection():
    """Cria conexão com o banco de dados PostgreSQL"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', 5432),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )


class ElVideoBotAgent(Agent):
    def __init__(self) -> None:
        # Montar instruções com base de conhecimento
        instructions = """Você é o Estevinho, um assistente virtual brasileiro amigável e analítico.

🎤 REGRA MAIS IMPORTANTE: SEMPRE FALE ANTES DE CHAMAR FERRAMENTAS!
- NUNCA execute ferramentas em silêncio
- SEMPRE diga o que vai fazer ANTES de fazer
- Chame APENAS UMA ferramenta por vez
- Comente o resultado ANTES de chamar a próxima
- Isso evita pausas dramáticas e mantém o usuário informado

Capacidades:
- Conversar naturalmente em português
- Gerar e exibir gráficos quando solicitado
- Responder perguntas usando a base de conhecimento abaixo
- Analisar dados e fornecer insights valiosos
- Sempre fale números por extenso (nove, dez, onze) na CONVERSA
- Mantenha respostas curtas e objetivas

REGRAS DE NÚMEROS:
1. **Na FALA (sua resposta de voz)**: Use números por extenso
   - Exemplo: "Temos oito mil quinhentos e cinquenta e seis funcionários ativos"
2. **Nos GRÁFICOS (parâmetro 'dados')**: Use números em algarismos
   - Exemplo: {"nome":"Funcionários","valor":8556}

IMPORTANTE sobre gráficos:
Quando usar a ferramenta gerar_grafico:
1. O parâmetro 'dados' DEVE ter valores NUMÉRICOS (algarismos): {"valor":8556}
2. Formato: '[{"nome":"Item1","valor":10},{"nome":"Item2","valor":20}]'
3. NUNCA use texto nos valores do gráfico

Exemplo de uso correto:
- tipo: "bar"
- titulo: "Arrecadação Municipal"
- dados: '[{"nome":"2023","valor":84332248.52},{"nome":"2024","valor":121355593.24}]'

COMPORTAMENTO APÓS GERAR GRÁFICO:
1. **Sempre comente** os dados exibidos no gráfico
2. **Forneça insights** relevantes (tendências, comparações, destaques)
3. **Explique** o que os dados significam em termos práticos
4. **Use números por extenso** na sua explicação verbal

MÚLTIPLOS GRÁFICOS:
- Você pode gerar ATÉ 3 GRÁFICOS de uma vez se necessário
- Para comparações, use múltiplos gráficos (ex: um de barras + um de pizza)
- Chame a ferramenta gerar_grafico múltiplas vezes na mesma resposta
- Comente todos os gráficos gerados de forma integrada

🗄️ BANCO DE DADOS - VOCÊ TEM ACESSO DIRETO!

IMPORTANTE: Você tem acesso a um banco PostgreSQL com 215 TABELAS em múltiplos schemas!

🔧 SUAS 3 FERRAMENTAS SQL:

1. **listar_tabelas_banco()** - SEMPRE comece por aqui quando pedirem análise do banco
   - Lista TODAS as 215 tabelas agrupadas por schema
   - Schemas: anatel, atricon, aws, bc, camara, catalogo, edu, etc.

2. **explorar_estrutura_tabela("schema.tabela")** - Veja colunas e tipos
   - Exemplo: explorar_estrutura_tabela("aws.cliente")
   - Exemplo: explorar_estrutura_tabela("camara.deputado")

3. **executar_query_customizada(query_sql, limite)** - Execute qualquer SELECT
   - Cria visualização ELEGANTE na tela automaticamente!
   - O resultado aparece em um card bonito no lado direito
   - Exemplos:
     * "SELECT COUNT(*) FROM aws.cliente"
     * "SELECT estado, COUNT(*) as total FROM aws.cliente GROUP BY estado ORDER BY total DESC"
     * "SELECT * FROM camara.deputado LIMIT 10"

🎯 FLUXO DE TRABALHO - SEMPRE FALE ANTES DE AGIR!

🚨 REGRA CRÍTICA: NUNCA chame ferramentas sem falar primeiro!

**FLUXO CORRETO:**
1. FALE o que vai fazer
2. CHAME UMA ferramenta
3. COMENTE o resultado
4. FALE o que vai fazer a seguir
5. CHAME a próxima ferramenta
6. REPITA até concluir

❌ ERRADO (NÃO faça assim):
- Chamar múltiplas ferramentas de uma vez sem falar
- Executar queries sem avisar antes
- Ficar em silêncio enquanto busca dados

✅ CORRETO (SEMPRE faça assim):

Usuário: "Analise a tabela aws.cliente"

Você FALA: "Vou explorar a estrutura da tabela aws ponto cliente para entender quais dados temos..."
→ Chama apenas 1 ferramenta: explorar_estrutura_tabela("aws.cliente")
→ Aguarda resultado

Você FALA: "Encontrei X colunas. Agora vou buscar quantos clientes temos no total..."
→ Chama apenas 1 ferramenta: executar_query_customizada("SELECT COUNT(*) FROM aws.cliente")
→ Aguarda resultado

Você FALA: "Temos Y clientes. Vou verificar a distribuição por estado..."
→ Chama apenas 1 ferramenta: executar_query_customizada("SELECT estado, COUNT(*)...")
→ Aguarda resultado

Você FALA: "Pronto! Encontrei que [insights]..."
→ NÃO chama mais ferramentas, apenas resume

⚠️ LIMITES:
- Máximo 3 tabelas por análise
- Máximo 2 queries por tabela
- SEMPRE fale antes de cada ferramenta
- NUNCA chame mais de 1 ferramenta por vez

📌 EXEMPLO PRÁTICO:

Usuário: "Analise meu banco de dados"

1️⃣ Você: "Vou listar as tabelas disponíveis..."
   → listar_tabelas_banco()

2️⃣ Você: "Encontrei duzentos e quinze tabelas! Vou analisar a tabela aws.cliente..."
   → explorar_estrutura_tabela("aws.cliente")
   → executar_query_customizada("SELECT COUNT(*) FROM aws.cliente")

   Você: "Temos X clientes. Vou ver a distribuição por estado..."
   → executar_query_customizada("SELECT estado, COUNT(*) as total FROM aws.cliente GROUP BY estado ORDER BY total DESC LIMIT 5")

3️⃣ Você: "Agora a tabela camara.deputado..."
   → explorar_estrutura_tabela("camara.deputado")
   → executar_query_customizada("SELECT COUNT(*) FROM camara.deputado")

4️⃣ Você: "Pronto! Resumi os principais insights do seu banco de dados."
   → PARA aqui, NÃO chama mais ferramentas

🚨 REGRAS CRÍTICAS:
- Máximo 3 tabelas por análise
- Máximo 2 queries por tabela
- SEMPRE pare após apresentar os insights
- NÃO repita queries já executadas
- As visualizações aparecem automaticamente quando você usa executar_query_customizada()

Exemplo de resposta após gerar gráfico:
"Exibindo o gráfico de arrecadação municipal. Observe que em dois mil e vinte e quatro
houve um crescimento de quarenta e três vírgula nove por cento em relação a dois mil e vinte e três,
saltando de oitenta e quatro milhões para cento e vinte e um milhões de reais.
Esse crescimento expressivo indica uma melhoria significativa na capacidade de arrecadação do município."

---
BASE DE CONHECIMENTO:
"""

        # Adicionar base de conhecimento se disponível
        if KNOWLEDGE_BASE:
            instructions += f"\n{KNOWLEDGE_BASE}\n---\n"

        instructions += """
INSTRUÇÕES FINAIS:
- Use os dados da base de conhecimento quando relevante
- Quando pedirem gráficos relacionados aos dados acima, use esses valores reais (em algarismos)
- Após gerar o gráfico, SEMPRE comente e analise os dados
- Forneça insights valiosos: tendências, comparações, pontos de atenção
- Lembre-se: números em algarismos no gráfico, por extenso na fala
- Seja analítico mas mantenha linguagem acessível

Exemplos de insights:
- "Destaco que o ISS representa quarenta e oito por cento da arrecadação, sendo nossa principal fonte"
- "Há uma tendência de crescimento de setenta e nove vírgula oito por cento no número de empresas"
- "A relação professor-aluno de um vírgula setenta e oito está acima da média nacional"
"""

        super().__init__(instructions=instructions)

    @function_tool()
    async def gerar_grafico(
        self,
        ctx: RunContext,
        tipo: Annotated[str, "Tipo: 'bar', 'line', 'pie' ou 'area'"],
        titulo: Annotated[str, "Título do gráfico"],
        dados: Annotated[
            str,
            'Array JSON com valores NUMÉRICOS (algarismos). Formato: [{"nome":"Item1","valor":10},{"nome":"Item2","valor":20.5}]. Valores podem ter decimais.'
        ],
    ) -> str:
        """Gera e exibe um gráfico na tela do usuário.

        IMPORTANTE:
        - Valores do gráfico devem ser NUMÉRICOS (algarismos): 10, 20.5, 8556
        - NÃO use texto nos valores: "dez", "vinte" etc
        - String JSON válida: '[{"nome":"Jan","valor":10},{"nome":"Fev","valor":15.5}]'

        APÓS GERAR: Sempre comente os dados e forneça insights na sua resposta verbal.
        Use números por extenso apenas na FALA, não no gráfico.

        Args:
            tipo: 'bar', 'line', 'pie' ou 'area'
            titulo: Título descritivo do gráfico
            dados: JSON array com nome (string) e valor (número)

        Returns:
            Mensagem confirmando que o gráfico foi exibido
        """
        try:
            # Parsear dados JSON
            dados_list = json.loads(dados)
            logger.info(f"Gerando gráfico {tipo} com {len(dados_list)} pontos de dados")

            # Criar payload do gráfico
            grafico_data = {
                "tipo": tipo,
                "titulo": titulo,
                "dados": dados_list
            }

            # Enviar via data channel do LiveKit
            room = get_job_context().room
            await room.local_participant.publish_data(
                json.dumps(grafico_data).encode('utf-8'),
                topic="grafico",
                reliable=True
            )

            logger.info(f"Gráfico enviado com sucesso: {titulo}")
            return f"Gráfico '{titulo}' exibido na tela com sucesso!"

        except Exception as e:
            logger.error(f"Erro ao gerar gráfico: {e}")
            return f"Erro ao gerar gráfico: {str(e)}"

    @function_tool()
    async def listar_tabelas_banco(self, ctx: RunContext) -> str:
        """Lista todas as tabelas disponíveis no banco de dados (todos os schemas).

        Use esta ferramenta quando o usuário perguntar:
        - "Quais tabelas temos?"
        - "O que tem no banco?"
        - "Mostre as tabelas"

        Returns:
            Lista de tabelas disponíveis (formato: schema.tabela)
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Buscar em TODOS os schemas, exceto schemas de sistema
            cursor.execute("""
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_type = 'BASE TABLE'
                AND table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
                ORDER BY table_schema, table_name;
            """)

            tables = cursor.fetchall()

            # Filtrar tabelas de sistema PostGIS
            tabelas_filtradas = [
                f"{schema}.{nome}"
                for schema, nome in tables
                if not nome.startswith('spatial_')
                and nome not in ('geography_columns', 'geometry_columns', 'raster_columns', 'raster_overviews')
            ]

            # Agrupar por schema
            schemas = {}
            for tabela in tabelas_filtradas:
                schema, nome = tabela.split('.')
                if schema not in schemas:
                    schemas[schema] = []
                schemas[schema].append(nome)

            cursor.close()
            conn.close()

            if tabelas_filtradas:
                resultado = f"✅ Encontrei {len(tabelas_filtradas)} tabelas em {len(schemas)} schemas:\n\n"

                # Mostrar agrupado por schema
                for schema, tabelas in sorted(schemas.items()):
                    resultado += f"📂 **{schema}** ({len(tabelas)} tabelas):\n"
                    resultado += f"   {', '.join(tabelas[:10])}"
                    if len(tabelas) > 10:
                        resultado += f"... (+{len(tabelas)-10} mais)"
                    resultado += "\n\n"

                resultado += "Use explorar_estrutura_tabela('schema.tabela') para ver a estrutura."
                return resultado
            else:
                return "Nenhuma tabela encontrada no banco de dados."

        except Exception as e:
            logger.error(f"Erro ao listar tabelas: {e}")
            return f"Erro ao listar tabelas: {str(e)}"

    @function_tool()
    async def explorar_estrutura_tabela(
        self,
        ctx: RunContext,
        nome_tabela: Annotated[str, "Nome da tabela a explorar (formato: schema.tabela ou apenas tabela)"],
    ) -> str:
        """Mostra a estrutura de uma tabela específica (colunas e tipos).

        Use esta ferramenta quando o usuário perguntar:
        - "Mostre a estrutura da tabela X"
        - "Quais colunas tem na tabela X?"
        - "O que tem na tabela X?"

        Args:
            nome_tabela: Nome da tabela (pode ser 'schema.tabela' ou apenas 'tabela')

        Returns:
            Estrutura da tabela com colunas e tipos
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Separar schema e tabela se fornecido
            if '.' in nome_tabela:
                schema, tabela = nome_tabela.split('.', 1)
            else:
                schema = None
                tabela = nome_tabela

            # Query com ou sem schema
            if schema:
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position;
                """, (schema, tabela))
            else:
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position;
                """, (tabela,))

            columns = cursor.fetchall()

            cursor.close()
            conn.close()

            if columns:
                estrutura = f"📊 Estrutura da tabela '{nome_tabela}':\n\n"
                for col in columns:
                    nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
                    estrutura += f"  • {col[0]} ({col[1]}) - {nullable}\n"

                estrutura += f"\nTotal de colunas: {len(columns)}"
                estrutura += f"\n\nAgora você pode consultar dados usando:\nexecutar_query_customizada('SELECT * FROM {nome_tabela} LIMIT 10')"
                return estrutura
            else:
                return f"❌ Tabela '{nome_tabela}' não encontrada.\n\nUse listar_tabelas_banco para ver as tabelas disponíveis."

        except Exception as e:
            logger.error(f"Erro ao explorar tabela: {e}")
            return f"Erro: {str(e)}"

    @function_tool()
    async def executar_query_customizada(
        self,
        ctx: RunContext,
        query_sql: Annotated[str, "Query SQL SELECT a executar. Apenas SELECT é permitido."],
        limite: Annotated[int, "Número máximo de resultados a retornar"] = 10,
    ) -> str:
        """Executa uma query SELECT customizada no banco de dados.

        IMPORTANTE:
        - Apenas queries SELECT são permitidas (segurança)
        - Use prepared statements para evitar SQL injection
        - Sempre adicione LIMIT para não sobrecarregar

        Exemplos de queries válidas:
        - "SELECT * FROM empresas WHERE status = 'ativa'"
        - "SELECT COUNT(*) FROM funcionarios"
        - "SELECT cidade, COUNT(*) as total FROM empresas GROUP BY cidade"
        - "SELECT SUM(valor) as total FROM arrecadacao WHERE ano = 2024"

        Args:
            query_sql: Query SQL SELECT
            limite: Máximo de resultados (padrão: 10, máximo: 100)

        Returns:
            Resultados da query em formato JSON
        """
        try:
            # Segurança: apenas SELECT
            if not query_sql.strip().upper().startswith('SELECT'):
                return "❌ Erro: Apenas queries SELECT são permitidas por segurança."

            # Limitar máximo de resultados
            if limite > 100:
                limite = 100

            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Adicionar LIMIT se não tiver
            if 'LIMIT' not in query_sql.upper():
                query_sql += f" LIMIT {limite}"

            logger.info(f"Executando query: {query_sql}")
            cursor.execute(query_sql)
            results = cursor.fetchall()

            # Pegar nomes das colunas
            if cursor.description:
                column_names = [desc[0] for desc in cursor.description]
            else:
                column_names = []

            cursor.close()
            conn.close()

            # Enviar visualização via data channel
            sql_visual_data = {
                "query": query_sql,
                "columns": column_names,
                "rows": results,
                "rowCount": len(results),
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }

            room = get_job_context().room
            await room.local_participant.publish_data(
                json.dumps(sql_visual_data, default=str, ensure_ascii=False).encode('utf-8'),
                topic="sql-result",
                reliable=True
            )

            logger.info(f"Resultado SQL enviado para visualização: {len(results)} registros")

            if results:
                # Se for uma agregação simples (COUNT, SUM, etc)
                if len(results) == 1 and len(results[0]) == 1:
                    valor = list(results[0].values())[0]
                    nome_campo = list(results[0].keys())[0]
                    return f"✅ Resultado exibido na tela: {nome_campo} = {valor}"

                # Múltiplos resultados
                return f"✅ Query executada! Exibindo {len(results)} registros na tela."
            else:
                return f"✅ Query executada mas não retornou resultados."

        except Exception as e:
            logger.error(f"Erro ao executar query: {e}")
            return f"❌ Erro ao executar query: {str(e)}\n\nQuery tentada: {query_sql}"


    async def on_enter(self):
        """Quando o agente entra na sessão, gera uma saudação"""
        await self.session.generate_reply(
            instructions="Diga olá ao usuário em português brasileiro de forma amigável e se apresente como Estevinho"
        )


async def entrypoint(ctx: JobContext):
    """Ponto de entrada principal do agente"""

    # ===== ANAM DESABILITADO PROVISORIAMENTE =====
    # Validar credenciais ANAM
    # anam_api_key = os.getenv("ANAM_API_KEY")
    # if not anam_api_key:
    #     raise ValueError("ANAM_API_KEY não está configurado no arquivo .env")

    # anam_avatar_id = os.getenv("ANAM_AVATAR_ID")
    # if not anam_avatar_id:
    #     raise ValueError("ANAM_AVATAR_ID não está configurado no arquivo .env")
    # ===== FIM ANAM DESABILITADO =====

    # Validar outras credenciais
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY não está configurado no arquivo .env")

    if not os.getenv("ELEVENLABS_API_KEY"):
        raise ValueError("ELEVENLABS_API_KEY não está configurado no arquivo .env")

    logger.info("Inicializando El Video Bot...")

    # Criar sessão do agente com pipeline personalizado
    # Usando OpenAI Whisper para STT (português), GPT-4o-mini para LLM, ElevenLabs para TTS
    session = AgentSession(
        stt=openai.STT(language="pt"),
        llm=openai.LLM(
            model="gpt-4o-mini",
            parallel_tool_calls=False,  # Desabilitar chamadas paralelas para evitar pausas dramáticas
        ),
        tts=elevenlabs.TTS(
            voice_id="GDzHdQOi6jjf8zaXhCYD",
            model="eleven_flash_v2_5",  # Modelo atualizado para v2.5
            language="pt",
            streaming_latency=3,  # Latência de streaming em segundos
            chunk_length_schedule=[80, 120, 200, 260],  # Tamanhos de chunk otimizados
        ),
        vad=silero.VAD.load(),  # Voice Activity Detection
    )

    # ===== ANAM DESABILITADO PROVISORIAMENTE =====
    # Inicializar avatar ANAM
    # logger.info(f"Inicializando avatar ANAM com ID: {anam_avatar_id}")
    # anam_avatar = anam.AvatarSession(
    #     persona_config=anam.PersonaConfig(
    #         name="El Video Bot",
    #         avatarId=anam_avatar_id,
    #     ),
    #     api_key=anam_api_key,
    #     avatar_participant_name=AGENT_NAME,
    # )

    # # Iniciar avatar na sala
    # await anam_avatar.start(session, room=ctx.room)
    # ===== FIM ANAM DESABILITADO =====

    # Iniciar sessão do agente
    await session.start(
        agent=ElVideoBotAgent(),
        room=ctx.room,
    )

    logger.info("El Video Bot iniciado com sucesso!")


async def request_fnc(req: JobRequest):
    """Função para aceitar requisições de jobs"""
    await req.accept(
        attributes={"agentType": "video-avatar"},
    )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            worker_type=WorkerType.ROOM,
            request_fnc=request_fnc,
            agent_name="el-video-bot"  # Nome usado para requisitar o agente
        )
    )
