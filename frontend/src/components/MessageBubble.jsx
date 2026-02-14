import ResultTable from './ResultTable';
import ChartDisplay from './ChartDisplay';
import FollowUpChips from './FollowUpChips';

/**
 * @param {{
 *   message: {
 *     role: 'user' | 'assistant' | 'loading',
 *     text?: string,
 *     summary?: { text: string, table: object, followups: string[] },
 *     chartSpec?: object,
 *     error?: string,
 *   },
 *   onFollowUp: (q: string) => void
 * }} props
 */
export default function MessageBubble({ message, onFollowUp }) {
  const { role } = message;

  if (role === 'user') {
    return (
      <div className="message message-user">
        {message.text}
      </div>
    );
  }

  if (role === 'loading') {
    return (
      <div className="message message-assistant">
        <div className="flex items-center gap-3 text-gray-400">
          <div className="loading" />
          <span>Processing your query...</span>
        </div>
      </div>
    );
  }

  if (role === 'error') {
    return (
      <div className="message message-assistant">
        <span className="text-red-400">❌ {message.error}</span>
      </div>
    );
  }

  // assistant
  const { summary, chartSpec } = message;
  const hasTable = summary?.table?.columns?.length && summary?.table?.rows?.length;
  const hasText  = summary?.text?.trim().length > 0;

  return (
    <div className="message message-assistant">
      {hasTable && <ResultTable table={summary.table} />}

      {hasText && (
        <div className="bg-gray-900 p-4 rounded-lg mt-3">
          <p className="text-gray-300 leading-relaxed">{summary.text}</p>
        </div>
      )}

      {chartSpec && <ChartDisplay chartSpec={chartSpec} />}

      {summary?.followups?.length > 0 && (
        <FollowUpChips questions={summary.followups} onSelect={onFollowUp} />
      )}

      {!hasTable && !hasText && !chartSpec && (
        <div className="text-gray-400">No results to display</div>
      )}
    </div>
  );
}
