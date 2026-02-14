const BASE_URL = 'http://localhost:8000/api';

/**
 * Uploads a CSV/Excel/image file and initialises a session.
 * @param {File} file
 * @returns {Promise<{ session_id: string, filename: string }>}
 */
export async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  const data = await response.json();
  if (data.status !== 'success') {
    throw new Error(data.message || 'Upload failed');
  }
  return data;
}

/**
 * Initialises a session from a database connection string or file path.
 * @param {string} connectionString
 * @returns {Promise<{ session_id: string }>}
 */
export async function initSession(connectionString) {
  const response = await fetch(`${BASE_URL}/init-session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file_path: connectionString }),
  });

  const data = await response.json();
  if (data.status !== 'success') {
    throw new Error(data.message || 'Connection failed');
  }
  return data;
}

/**
 * Sends a natural-language query for an active session.
 * @param {string} sessionId
 * @param {string} query
 * @returns {Promise<{ summary: object, chart_url: string|null }>}
 */
export async function sendQuery(sessionId, query) {
  const response = await fetch(`${BASE_URL}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, query }),
  });

  const data = await response.json();
  if (data.status !== 'success') {
    throw new Error(data.message || 'Query failed');
  }
  return data;
}
