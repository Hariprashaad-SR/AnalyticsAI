import { useEffect, useRef } from 'react';

/**
 * @param {{ value: string, onChange: (v: string) => void, onSubmit: () => void, disabled: boolean }} props
 */
export default function ChatInput({ value, onChange, onSubmit, disabled }) {
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  function handleSubmit(e) {
    e.preventDefault();
    if (!disabled) onSubmit();
  }

  return (
    <div className="chat-input-area">
      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="chat-input flex-1"
          placeholder="Ask a question about your data..."
          autoComplete="off"
          disabled={disabled}
        />
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className="btn btn-primary px-6 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </form>
    </div>
  );
}
