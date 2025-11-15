# El Video Bot

Assistente virtual em português com avatar animado ANAM. Recebe áudio em português, transcreve com OpenAI Whisper, analisa com GPT-4o-mini, gera resposta e converte para vídeo com avatar ANAM e áudio em português via ElevenLabs.

## Arquitetura

```
Áudio (PT-BR) → OpenAI Whisper (STT) → Texto →
GPT-4o-mini (LLM) → Resposta →
ElevenLabs (TTS PT-BR) + ANAM Avatar →
Vídeo com áudio sincronizado
```

## Tecnologias

- **STT:** OpenAI Whisper (português brasileiro)
- **LLM:** OpenAI GPT-4o-mini
- **TTS:** ElevenLabs (voz multilíngue em português)
- **Avatar:** ANAM (vídeo animado do avatar)
- **Framework:** LiveKit Agents
- **Frontend:** Next.js 15 com React 19

## Pré-requisitos

- Python 3.10+
- Node.js 18+ e pnpm
- Credenciais:
  - LiveKit Cloud (URL, API Key, API Secret)
  - OpenAI API Key
  - ElevenLabs API Key
  - ANAM API Key e Avatar ID

## Instalação

### 1. Backend (Agente Python)

```bash
# Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Frontend (Next.js)

```bash
cd frontend
pnpm install
```

## Configuração

### Backend (.env)

O arquivo `.env` já está configurado com:

```env
# LiveKit Cloud
LIVEKIT_URL=wss://feira-tt890ert.livekit.cloud
LIVEKIT_API_KEY=APIpG23yC3Vipuj
LIVEKIT_API_SECRET=yhJuIVmH8kYgaAmfV9LAf4GCY4KuwRe6gDLdDkeXa5rA

# OpenAI (STT Whisper + LLM GPT-4o-mini)
OPENAI_API_KEY=sk-proj-...

# ElevenLabs (TTS em português)
ELEVENLABS_API_KEY=353d3b755f5da88c65afa9e29789e2ce...

# ANAM Avatar
ANAM_API_KEY=NDBhZGU3NTItMTYzNy00MGM4...
ANAM_AVATAR_ID=edf6fdcb-acab-44b8-b974-ded72665ee26
```

### Frontend (.env.local)

O arquivo `frontend/.env.local` já está configurado com:

```env
LIVEKIT_URL=wss://feira-tt890ert.livekit.cloud
LIVEKIT_API_KEY=APIpG23yC3Vipuj
LIVEKIT_API_SECRET=yhJuIVmH8kYgaAmfV9LAf4GCY4KuwRe6gDLdDkeXa5rA
NEXT_PUBLIC_AGENT_NAME=el-video-bot
```

## Executar

### IMPORTANTE: Escolha da Versão

Existem 2 versões do agente:

#### 1. `agent.py` - Versão com ElevenLabs (EXPERIMENTAL)
- ✅ Usa ElevenLabs para TTS (vozes mais naturais em português)
- ✅ Usa GPT-4o-mini (mais econômico)
- ⚠️ Pode não funcionar com ANAM (incompatibilidade de pipeline)

#### 2. `agent_realtime.py` - Versão com OpenAI Realtime (GARANTIDA)
- ✅ Funcionamento 100% garantido com ANAM
- ✅ Integração nativa STT + LLM + TTS
- ⚠️ Usa TTS da OpenAI (vozes em inglês, mas fala português)
- ⚠️ Usa GPT-4o-realtime (pode ser mais caro)

**Recomendação:** Comece com `agent_realtime.py` para garantir que funciona. Se quiser testar ElevenLabs, tente `agent.py` depois.

### 1. Iniciar o Backend (Terminal 1)

**Versão Garantida (Recomendada para primeiro teste):**
```bash
python agent_realtime.py dev
```

**OU Versão com ElevenLabs (Experimental):**
```bash
python agent.py dev
```

Você verá:
```
INFO:el-video-bot:Inicializando El Video Bot...
INFO:el-video-bot:Inicializando avatar ANAM com ID: edf6fdcb-acab-44b8-b974-ded72665ee26
INFO:el-video-bot:El Video Bot iniciado com sucesso!
```

### 2. Iniciar o Frontend (Terminal 2)

```bash
cd frontend
pnpm dev
```

Abra http://localhost:3000 no navegador.

## Como Usar

1. Acesse http://localhost:3000
2. Clique em "Iniciar conversa"
3. Permita acesso ao microfone quando solicitado
4. Comece a falar em português
5. O avatar ANAM aparecerá na tela e responderá com voz e vídeo animado

## Fluxo de Conversação

1. **Você fala** em português → Microfone captura áudio
2. **OpenAI Whisper** transcreve → Texto em português
3. **GPT-4o-mini** processa → Gera resposta inteligente
4. **ElevenLabs** sintetiza → Áudio em português com voz natural
5. **ANAM Avatar** anima → Vídeo sincronizado com o áudio
6. **Você vê e ouve** a resposta com avatar animado

## Customização

### Trocar Voz ElevenLabs

No arquivo `agent.py`, linha ~66:

```python
tts=elevenlabs.TTS(
    voice="Bella",  # Altere para outra voz: "Adam", "Nicole", etc.
    model="eleven_multilingual_v2",
),
```

Vozes populares em português:
- **Bella** - Feminina, clara
- **Matilda** - Feminina, jovem
- **Nicole** - Feminina, madura
- **Adam** - Masculina, grave

### Personalizar Instruções do Agente

No arquivo `agent.py`, classe `ElVideoBotAgent`, linha ~31:

```python
instructions="""Você é um assistente virtual amigável e prestativo que fala português brasileiro.
Mantenha suas respostas concisas e conversacionais.
Seja natural e empático em suas interações.""",
```

Exemplos de personalização:
```python
# Assistente educacional
instructions="""Você é um professor de português brasileiro, paciente e didático.
Explique conceitos de forma clara e use exemplos práticos."""

# Assistente de vendas
instructions="""Você é um consultor de vendas amigável.
Ajude os clientes a encontrar produtos e tire dúvidas."""

# Recepcionista virtual
instructions="""Você é uma recepcionista virtual educada e profissional.
Cumprimente os visitantes e direcione-os conforme necessário."""
```

### Ajustar Modelo LLM

Para usar GPT-4 em vez de GPT-4o-mini (mais inteligente, mas mais caro):

```python
llm=openai.LLM(model="gpt-4"),  # Mais inteligente
# ou
llm=openai.LLM(model="gpt-3.5-turbo"),  # Mais rápido e econômico
```

## Qual Versão Usar?

### Use `agent_realtime.py` se:
- ✅ Quer garantia de funcionamento (primeira vez testando)
- ✅ Não se importa com a voz ser da OpenAI
- ✅ Precisa de estabilidade máxima

### Use `agent.py` se:
- ✅ Quer vozes mais naturais em português (ElevenLabs)
- ✅ Quer controle total sobre STT/LLM/TTS
- ✅ Está disposto a testar e resolver possíveis incompatibilidades

## Estrutura do Projeto

```
el_video_bot/
├── agent.py              # Agente com ElevenLabs (experimental)
├── agent_realtime.py     # Agente com OpenAI Realtime (garantido)
├── requirements.txt      # Dependências Python
├── .env                  # Credenciais backend
├── README.md             # Este arquivo
└── frontend/
    ├── app/              # Next.js App Router
    ├── components/       # Componentes React
    ├── lib/              # Utilitários
    ├── public/           # Assets estáticos
    ├── package.json      # Dependências Node.js
    ├── .env.local        # Credenciais frontend
    └── app-config.ts     # Configuração do app
```

## Troubleshooting

### Erro: "ANAM_API_KEY não está configurado"
Verifique se o arquivo `.env` existe e contém todas as credenciais.

### Avatar não aparece
1. Confirme que o agente Python está rodando (`python agent.py dev`)
2. Verifique se o `ANAM_AVATAR_ID` está correto
3. Confira os logs do terminal para erros

### Áudio não funciona
1. Permita acesso ao microfone no navegador
2. Verifique se a `ELEVENLABS_API_KEY` é válida
3. Teste com outra voz se necessário

### Frontend não conecta
1. Verifique se ambos backend e frontend estão rodando
2. Confirme que `NEXT_PUBLIC_AGENT_NAME` no `.env.local` é `el-video-bot`
3. Verifique se as credenciais LiveKit estão corretas

## Próximos Passos

- [ ] Adicionar funcionalidades customizadas com function tools
- [ ] Implementar histórico de conversação
- [ ] Adicionar suporte a múltiplos idiomas
- [ ] Integrar com banco de dados para persistência
- [ ] Deploy em produção no LiveKit Cloud

## Recursos

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [ElevenLabs API Documentation](https://elevenlabs.io/docs)
- [ANAM Documentation](https://docs.anam.ai/)

## Licença

Este projeto é baseado nos exemplos do LiveKit e está disponível para uso e modificação.
