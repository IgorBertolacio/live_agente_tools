import React from 'react';
import { motion } from 'framer-motion';
import { X, Database, Calendar, Table2 } from 'lucide-react';

interface SqlResultData {
  query: string;
  columns: string[];
  rows: Record<string, any>[];
  rowCount: number;
  timestamp: string;
}

interface SqlResultDisplayProps {
  data: SqlResultData;
  onClose?: () => void;
}

export const SqlResultDisplay: React.FC<SqlResultDisplayProps> = ({ data, onClose }) => {
  const { query, columns, rows, rowCount, timestamp } = data;

  // Formatar timestamp
  const formattedTime = new Date(timestamp).toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });

  // Detectar se é agregação simples (COUNT, SUM, etc)
  const isAggregation = rows.length === 1 && columns.length === 1;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      transition={{ duration: 0.3 }}
      className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl shadow-2xl border border-slate-700 overflow-hidden"
      style={{ maxWidth: '800px', width: '100%' }}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-white/20 p-2 rounded-lg">
            <Database className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-white font-semibold text-lg">Consulta SQL</h3>
            <div className="flex items-center gap-2 text-blue-100 text-xs mt-1">
              <Calendar className="w-3 h-3" />
              <span>{formattedTime}</span>
              <span className="mx-1">•</span>
              <Table2 className="w-3 h-3" />
              <span>{rowCount} registro{rowCount !== 1 ? 's' : ''}</span>
            </div>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="bg-white/10 hover:bg-white/20 p-2 rounded-lg transition-colors"
            aria-label="Fechar"
          >
            <X className="w-5 h-5 text-white" />
          </button>
        )}
      </div>

      {/* Query SQL */}
      <div className="px-6 py-4 bg-slate-950 border-b border-slate-700">
        <pre className="text-xs text-emerald-400 font-mono overflow-x-auto whitespace-pre-wrap">
          {query}
        </pre>
      </div>

      {/* Resultados */}
      <div className="p-6">
        {isAggregation ? (
          // Exibição especial para agregações (COUNT, SUM, etc)
          <div className="text-center py-8">
            <div className="inline-block bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl px-8 py-6 shadow-lg">
              <div className="text-emerald-100 text-sm font-medium mb-2">
                {columns[0]}
              </div>
              <div className="text-white text-5xl font-bold">
                {typeof rows[0][columns[0]] === 'number'
                  ? rows[0][columns[0]].toLocaleString('pt-BR')
                  : rows[0][columns[0]]
                }
              </div>
            </div>
          </div>
        ) : (
          // Tabela para múltiplos resultados
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  {columns.map((col, idx) => (
                    <th
                      key={idx}
                      className="text-left px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider"
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row, rowIdx) => (
                  <tr
                    key={rowIdx}
                    className="border-b border-slate-800 hover:bg-slate-800/50 transition-colors"
                  >
                    {columns.map((col, colIdx) => (
                      <td
                        key={colIdx}
                        className="px-4 py-3 text-sm text-slate-300"
                      >
                        {row[col] === null ? (
                          <span className="text-slate-500 italic">null</span>
                        ) : typeof row[col] === 'number' ? (
                          <span className="font-mono text-emerald-400">
                            {row[col].toLocaleString('pt-BR')}
                          </span>
                        ) : typeof row[col] === 'boolean' ? (
                          <span className={row[col] ? 'text-emerald-400' : 'text-rose-400'}>
                            {row[col] ? 'true' : 'false'}
                          </span>
                        ) : (
                          <span className="truncate block max-w-xs" title={String(row[col])}>
                            {String(row[col])}
                          </span>
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Scroll hint */}
            {rows.length > 5 && (
              <div className="text-center mt-4 text-xs text-slate-500">
                Role para ver mais registros
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      {!isAggregation && (
        <div className="px-6 py-3 bg-slate-950 border-t border-slate-700 text-xs text-slate-400 flex justify-between">
          <span>{columns.length} coluna{columns.length !== 1 ? 's' : ''}</span>
          <span>{rowCount} registro{rowCount !== 1 ? 's' : ''} exibido{rowCount !== 1 ? 's' : ''}</span>
        </div>
      )}
    </motion.div>
  );
};
