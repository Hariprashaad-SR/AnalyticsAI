import { useEffect, useRef, useState } from 'react';
import { sendQuery } from '../services/analyticsService';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';

/**
 * @param {{ sessionId: string, sourceName: string, onReset: () => void }} props
 */
export default function ChatScreen({ sessionId, sourceName, onReset }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Scroll to bottom whenever messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /** Adds a message object to the list */
  function addMessage(msg) {
    setMessages((prev) => [...prev, { id: Date.now() + Math.random(), ...msg }]);
  }

  async function handleSend() {
    const query = inputValue.trim();
    if (!query || !sessionId || isLoading) return;

    setInputValue('');
    addMessage({ role: 'user', text: query });
    setIsLoading(true);

    try {
      const data = await sendQuery(sessionId, query);

      // Parse chart spec if present
      let chartSpec = null;
      if (data.chart_url) {
        try {
          chartSpec = JSON.parse(data.chart_url);
        } catch {
          // ignore parse errors
        }
      }

      addMessage({ role: 'assistant', summary: data.summary, chartSpec });
    } catch (err) {
      addMessage({ role: 'error', error: err.message });
    } finally {
      setIsLoading(false);
    }
  }

  /** Called by FollowUpChips */
  function handleFollowUp(question) {
    setInputValue(question);
  }

  return (
    <div className="chat-single-column">
      <div className="chat-main">
        {/* Header */}
        <div className="chat-header">
          <div className="flex justify-between items-center">
            <div>
              <div className="text-sm text-gray-400">Source:</div>
              <div className="text-sm mono break-all">{sourceName || '—'}</div>
            </div>
            <button onClick={onReset} className="btn btn-secondary text-sm">
              New Session
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="text-center text-gray-400 py-8">
              <p className="text-lg">👋 Ready to analyse your data</p>
              <p className="text-sm mt-2">Ask me anything about your data using natural language</p>
            </div>
          )}

          {messages.map((msg) => (
            <MessageBubble
              key={msg.id}
              message={msg}
              onFollowUp={handleFollowUp}
            />
          ))}

          {isLoading && (
            <MessageBubble
              message={{ role: 'loading' }}
              onFollowUp={() => {}}
            />
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <ChatInput
          value={inputValue}
          onChange={setInputValue}
          onSubmit={handleSend}
          disabled={isLoading}
        />
      </div>
    </div>
  );
}
