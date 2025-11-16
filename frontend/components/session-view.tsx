'use client';

import React, { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import {
  type AgentState,
  type ReceivedChatMessage,
  useRoomContext,
  useVoiceAssistant,
} from '@livekit/components-react';
import { toastAlert } from '@/components/alert-toast';
import { AgentControlBar } from '@/components/livekit/agent-control-bar/agent-control-bar';
import { ChatEntry } from '@/components/livekit/chat/chat-entry';
import { ChatMessageView } from '@/components/livekit/chat/chat-message-view';
import { MediaTiles } from '@/components/livekit/media-tiles';
import { ChartDisplay, type ChartData } from '@/components/chart-display';
import { SqlResultDisplay } from '@/components/sql-result-display';
import useChatAndTranscription from '@/hooks/useChatAndTranscription';
import { useDebugMode } from '@/hooks/useDebug';
import useTextStreamLogger from '@/hooks/useTextStreamLogger';
import { cn } from '@/lib/utils';
import { DataPacket_Kind } from 'livekit-client';

interface SqlResultData {
  query: string;
  columns: string[];
  rows: Record<string, any>[];
  rowCount: number;
  timestamp: string;
}

function isAgentAvailable(agentState: AgentState) {
  return agentState == 'listening' || agentState == 'thinking' || agentState == 'speaking';
}

interface SessionViewProps {
  disabled: boolean;
  capabilities: {
    supportsChatInput: boolean;
    supportsVideoInput: boolean;
    supportsScreenShare: boolean;
  };
  sessionStarted: boolean;
}

export const SessionView = ({
  disabled,
  capabilities,
  sessionStarted,
  ref,
}: React.ComponentProps<'div'> & SessionViewProps) => {
  const { state: agentState } = useVoiceAssistant();
  const [chatOpen, setChatOpen] = useState(false);
  const { messages, send } = useChatAndTranscription();
  const room = useRoomContext();
  const [charts, setCharts] = useState<ChartData[]>([]);
  const [sqlResults, setSqlResults] = useState<SqlResultData[]>([]);

  useDebugMode();
  useTextStreamLogger();

  // Listener para receber dados de gráficos via data channel
  useEffect(() => {
    if (!room) {
      console.log('[CHART] Room não disponível ainda');
      return;
    }

    console.log('[CHART] Registrando listener de data channel');

    const handleDataReceived = (
      payload: Uint8Array,
      participant?: any,
      kind?: DataPacket_Kind,
      topic?: string
    ) => {
      console.log('[CHART] Data received - topic:', topic);

      const decoder = new TextDecoder();

      // Verificar se é um gráfico
      if (topic === 'grafico') {
        try {
          const jsonString = decoder.decode(payload);
          console.log('[CHART] JSON recebido:', jsonString);

          const chartData: ChartData = JSON.parse(jsonString);
          console.log('[CHART] Gráfico parseado:', chartData);

          // Adicionar gráfico (máximo 3)
          setCharts((prev) => {
            const updated = [...prev, chartData];
            // Manter apenas os últimos 3 gráficos
            if (updated.length > 3) {
              console.log('[CHART] Limite de 3 gráficos atingido, removendo o mais antigo');
              return updated.slice(-3);
            }
            console.log('[CHART] Total de gráficos:', updated.length);
            return updated;
          });
        } catch (error) {
          console.error('[CHART] Erro ao processar gráfico:', error);
        }
      }

      // Verificar se é um resultado SQL
      if (topic === 'sql-result') {
        try {
          const jsonString = decoder.decode(payload);
          console.log('[SQL] JSON recebido:', jsonString);

          const sqlData: SqlResultData = JSON.parse(jsonString);
          console.log('[SQL] Resultado SQL parseado:', sqlData);

          // Adicionar resultado SQL (máximo 2)
          setSqlResults((prev) => {
            const updated = [...prev, sqlData];
            // Manter apenas os últimos 2 resultados
            if (updated.length > 2) {
              console.log('[SQL] Limite de 2 resultados atingido, removendo o mais antigo');
              return updated.slice(-2);
            }
            console.log('[SQL] Total de resultados SQL:', updated.length);
            return updated;
          });
        } catch (error) {
          console.error('[SQL] Erro ao processar resultado SQL:', error);
        }
      }
    };

    room.on('dataReceived', handleDataReceived);
    console.log('[CHART] Listener registrado com sucesso');

    return () => {
      console.log('[CHART] Removendo listener');
      room.off('dataReceived', handleDataReceived);
    };
  }, [room]);

  async function handleSendMessage(message: string) {
    await send(message);
  }

  useEffect(() => {
    if (sessionStarted) {
      const timeout = setTimeout(() => {
        if (!isAgentAvailable(agentState)) {
          const reason =
            agentState === 'connecting'
              ? 'Agent did not join the room. '
              : 'Agent connected but did not complete initializing. ';

          toastAlert({
            title: 'Session ended',
            description: (
              <p className="w-full">
                {reason}
                <a
                  target="_blank"
                  rel="noopener noreferrer"
                  href="https://docs.livekit.io/agents/start/voice-ai/"
                  className="whitespace-nowrap underline"
                >
                  See quickstart guide
                </a>
                .
              </p>
            ),
          });
          room.disconnect();
        }
      }, 10_000);

      return () => clearTimeout(timeout);
    }
  }, [agentState, sessionStarted, room]);

  return (
    <main
      ref={ref}
      inert={disabled}
      className={
        // prevent page scrollbar
        // when !chatOpen due to 'translate-y-20'
        cn(!chatOpen && 'max-h-svh overflow-hidden')
      }
    >
      {/* Bloco de Resultados SQL - Lado Direito (até 2 resultados) */}
      <AnimatePresence>
        {sqlResults.length > 0 && (
          <motion.div
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 100 }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            className="fixed right-4 top-32 z-40 w-full max-w-2xl space-y-4"
          >
            {/* Botão para limpar todos os resultados */}
            <button
              onClick={() => setSqlResults([])}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90 absolute -top-3 -left-3 z-50 rounded-full p-2 shadow-lg transition-colors"
              aria-label="Fechar todos os resultados SQL"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>

            {/* Renderizar até 2 resultados SQL */}
            <div className="space-y-3">
              {sqlResults.map((result, index) => (
                <motion.div
                  key={`sql-${index}-${result.timestamp}`}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="relative"
                >
                  <SqlResultDisplay
                    data={result}
                    onClose={() => setSqlResults((prev) => prev.filter((_, i) => i !== index))}
                  />
                </motion.div>
              ))}
            </div>

            {/* Indicador de quantidade */}
            {sqlResults.length > 0 && (
              <div className="bg-muted text-muted-foreground mt-2 rounded-md p-2 text-center text-xs">
                {sqlResults.length} de 2 consulta{sqlResults.length !== 1 ? 's' : ''}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Bloco de Gráficos - Lado Esquerdo (até 3 gráficos) */}
      <AnimatePresence>
        {charts.length > 0 && (
          <motion.div
            initial={{ opacity: 0, x: -100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -100 }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            className="fixed left-4 top-32 z-40 w-full max-w-md space-y-4 md:max-w-lg"
          >
            {/* Botão para limpar todos os gráficos */}
            <button
              onClick={() => setCharts([])}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90 absolute -top-3 -right-3 z-50 rounded-full p-2 shadow-lg transition-colors"
              aria-label="Fechar todos os gráficos"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>

            {/* Renderizar até 3 gráficos */}
            <div className="space-y-3">
              {charts.map((chart, index) => (
                <motion.div
                  key={`chart-${index}-${chart.titulo}`}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="relative"
                >
                  {/* Botão para remover gráfico individual */}
                  <button
                    onClick={() => setCharts((prev) => prev.filter((_, i) => i !== index))}
                    className="bg-muted text-muted-foreground hover:bg-muted/80 absolute -top-2 -right-2 z-10 rounded-full p-1.5 shadow-md transition-colors"
                    aria-label={`Fechar gráfico ${index + 1}`}
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <line x1="18" y1="6" x2="6" y2="18"></line>
                      <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                  </button>

                  {/* Badge com número do gráfico */}
                  {charts.length > 1 && (
                    <div className="bg-primary text-primary-foreground absolute -top-2 -left-2 z-10 flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold shadow-md">
                      {index + 1}
                    </div>
                  )}

                  <ChartDisplay data={chart} />
                </motion.div>
              ))}
            </div>

            {/* Indicador de quantidade */}
            {charts.length > 0 && (
              <div className="bg-muted text-muted-foreground mt-2 rounded-md p-2 text-center text-xs">
                {charts.length} de 3 gráfico{charts.length !== 1 ? 's' : ''}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      <ChatMessageView
        className={cn(
          'mx-auto min-h-svh w-full max-w-2xl px-3 pt-32 pb-40 transition-[opacity,translate] duration-300 ease-out md:px-0 md:pt-36 md:pb-48',
          chatOpen ? 'translate-y-0 opacity-100 delay-200' : 'translate-y-20 opacity-0'
        )}
      >
        <div className="space-y-3 whitespace-pre-wrap">
          <AnimatePresence>
            {messages.map((message: ReceivedChatMessage) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 1, height: 'auto', translateY: 0.001 }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
              >
                <ChatEntry hideName key={message.id} entry={message} />
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </ChatMessageView>

      <div className="bg-background mp-12 fixed top-0 right-0 left-0 h-32 md:h-36">
        {/* skrim */}
        <div className="from-background absolute bottom-0 left-0 h-12 w-full translate-y-full bg-gradient-to-b to-transparent" />
      </div>

      <MediaTiles chatOpen={chatOpen} />

      <div className="bg-background fixed right-0 bottom-0 left-0 z-50 px-3 pt-2 pb-3 md:px-12 md:pb-12">
        <motion.div
          key="control-bar"
          initial={{ opacity: 0, translateY: '100%' }}
          animate={{
            opacity: sessionStarted ? 1 : 0,
            translateY: sessionStarted ? '0%' : '100%',
          }}
          transition={{ duration: 0.3, delay: sessionStarted ? 0.5 : 0, ease: 'easeOut' }}
        >
          <div className="relative z-10 mx-auto w-full max-w-2xl">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{
                opacity: sessionStarted && messages.length === 0 ? 1 : 0,
                transition: {
                  ease: 'easeIn',
                  delay: messages.length > 0 ? 0 : 0.8,
                  duration: messages.length > 0 ? 0.2 : 0.5,
                },
              }}
              aria-hidden={messages.length > 0}
              className={cn(
                'absolute inset-x-0 -top-12 text-center',
                sessionStarted && messages.length === 0 && 'pointer-events-none'
              )}
            >
              <p className="animate-text-shimmer inline-block !bg-clip-text text-sm font-semibold text-transparent">
                Agent is listening, ask it a question
              </p>
            </motion.div>

            <AgentControlBar
              capabilities={capabilities}
              onChatOpenChange={setChatOpen}
              onSendMessage={handleSendMessage}
            />
          </div>
          {/* skrim */}
          <div className="from-background border-background absolute top-0 left-0 h-12 w-full -translate-y-full bg-gradient-to-t to-transparent" />
        </motion.div>
      </div>
    </main>
  );
};
