/**
 * @param {{ questions: string[], onSelect: (q: string) => void }} props
 */
export default function FollowUpChips({ questions, onSelect }) {
  if (!questions?.length) return null;

  return (
    <div className="mt-4">
      <p className="text-gray-400 mb-2 text-sm">You can also ask:</p>
      <div className="flex flex-wrap gap-2">
        {questions.map((q, i) => (
          <button
            key={i}
            onClick={() => onSelect(q)}
            className="px-3 py-1.5 rounded-full bg-gray-800 border border-gray-700
                       text-gray-200 text-sm hover:bg-gray-700 transition"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
