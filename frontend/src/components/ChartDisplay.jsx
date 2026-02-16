import { useEffect, useRef, useState } from 'react';

/**
 * @param {{ chartSpec: object }} props  
 */
export default function ChartDisplay({ chartSpec }) {
  const [visible, setVisible] = useState(false);
  const plotRef = useRef(null);
  const renderedRef = useRef(false);

  useEffect(() => {
    if (visible && !renderedRef.current && plotRef.current && window.Plotly) {
      window.Plotly.newPlot(plotRef.current, chartSpec.data, chartSpec.layout, {
        responsive: true,
      });
      renderedRef.current = true;
    }
  }, [visible, chartSpec]);

  return (
    <div className="mt-4 border border-gray-700 rounded-lg overflow-hidden">
      <button
        onClick={() => setVisible((v) => !v)}
        className="w-full flex justify-between items-center px-4 py-2
                   bg-gray-800 text-gray-200 hover:bg-gray-700 transition"
      >
        <span>{visible ? 'Hide chart' : 'Show chart'}</span>
        <span className="text-sm opacity-70">{visible ? '▲' : '▼'}</span>
      </button>

      {visible && (
        <div className="bg-gray-900 p-3">
          <div ref={plotRef} className="w-full" style={{ height: 450 }} />
        </div>
      )}
    </div>
  );
}
