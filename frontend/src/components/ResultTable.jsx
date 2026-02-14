import { useState } from 'react';

/**
 * @param {{ columns: string[], rows: (string|number)[][] }} table
 */
export default function ResultTable({ table }) {
  const [filter, setFilter] = useState('');

  if (!table?.columns?.length || !table?.rows?.length) return null;

  const lower = filter.toLowerCase();
  const filtered = lower
    ? table.rows.filter((row) =>
        row.some((cell) => String(cell).toLowerCase().includes(lower))
      )
    : table.rows;

  return (
    <div className="mt-4 space-y-3">
      <input
        type="text"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        placeholder="Filter rows..."
        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md
                   text-gray-200 placeholder-gray-400 focus:outline-none"
      />

      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-700 rounded-lg">
          <thead className="bg-gray-800">
            <tr>
              {table.columns.map((col) => (
                <th
                  key={col}
                  className="px-4 py-2 text-left border-b border-gray-700 text-gray-300 text-sm"
                >
                  {col.replace(/_/g, ' ').toUpperCase()}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((row, ri) => (
              <tr key={ri} className="hover:bg-gray-900">
                {row.map((cell, ci) => (
                  <td key={ci} className="px-4 py-2 border-b border-gray-800 text-gray-200 text-sm">
                    {cell ?? '—'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filtered.length === 0 && (
        <p className="text-center text-gray-500 py-4 text-sm">No matching rows</p>
      )}
    </div>
  );
}
