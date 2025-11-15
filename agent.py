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
)
from livekit.plugins import openai, elevenlabs, silero  # , anam  # DESABILITADO PROVISORIAMENTE

logger = logging.getLogger("el-video-bot")
logger.setLevel(logging.INFO)

load_dotenv()

AGENT_NAME = "El Video Bot"


class ElVideoBotAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=""" Sempre gere numeros com letras exemplo nove dez onze, sempre gere somente texto descritivo e resumido você esta em um chatbot entao nao coloque nada alem de texto""",
        )

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
        llm=openai.LLM(model="gpt-4o-mini"),
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
