import { useRef, useState } from 'react';
import { uploadFile, initSession } from '../services/analyticsService';

const UploadIcon = () => (
  <svg className="mx-auto mb-4" width="64" height="64" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="1.5">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"
      stroke="#ffffff" />
  </svg>
);

const STATUS = { idle: 'idle', loading: 'loading', success: 'success', error: 'error' };

export default function UploadScreen({ onSessionReady }) {
  const fileInputRef = useRef(null);
  const [dbValue, setDbValue] = useState('');
  const [dragover, setDragover] = useState(false);
  const [status, setStatus] = useState({ type: STATUS.idle, message: '' });

  /* ── helpers ── */
  const setLoading = (msg) => setStatus({ type: STATUS.loading, message: msg });
  const setSuccess = (msg) => setStatus({ type: STATUS.success, message: msg });
  const setError   = (msg) => setStatus({ type: STATUS.error,   message: msg });

  /* ── file upload ── */
  async function handleFileChange(e) {
    const file = e.target.files[0];
    if (!file) return;

    setLoading('Uploading...');
    try {
      const data = await uploadFile(file);
      setSuccess('✓ File uploaded successfully!');
      setTimeout(() => onSessionReady(data.session_id, data.filename), 1000);
    } catch (err) {
      setError('✗ ' + err.message);
    }
  }

  /* ── DB connection ── */
  async function handleConnect() {
    if (!dbValue.trim()) {
      alert('Please enter a database connection string');
      return;
    }
    setLoading('Connecting...');
    try {
      const data = await initSession(dbValue.trim());
      setSuccess('✓ Connected successfully!');
      setTimeout(() => onSessionReady(data.session_id, dbValue.trim()), 1000);
    } catch (err) {
      setError('✗ ' + err.message);
    }
  }

  /* ── drag & drop ── */
  function handleDrop(e) {
    e.preventDefault();
    setDragover(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      fileInputRef.current.files = files;
      fileInputRef.current.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }

  /* ── status banner ── */
  const statusBannerStyle = () => {
    if (status.type === STATUS.success)
      return { background: 'rgba(255,255,255,0.1)', borderColor: '#ffffff' };
    if (status.type === STATUS.error)
      return { background: 'rgba(255,68,68,0.2)', borderColor: '#ff4444' };
    return {};
  };

  return (
    <div>
      {/* Drop zone */}
      <div
        className={`upload-zone ${dragover ? 'dragover' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragover(true); }}
        onDragLeave={() => setDragover(false)}
        onDrop={handleDrop}
      >
        <UploadIcon />
        <h2 className="text-2xl font-semibold mb-3">Upload Your Data Source</h2>
        <p className="text-gray-400 mb-6">Drop your CSV, Excel, or enter a database connection string</p>

        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls,.webp,.png"
          className="hidden"
          onChange={handleFileChange}
        />
        <button
          className="btn btn-primary mb-4"
          onClick={() => fileInputRef.current.click()}
        >
          Choose File
        </button>

        <div className="my-6 text-gray-500">— OR —</div>

        <input
          type="text"
          value={dbValue}
          onChange={(e) => setDbValue(e.target.value)}
          placeholder="postgresql://user:pass@host:5432/db"
          className="mb-4"
        />
        <button className="btn btn-secondary" onClick={handleConnect}>
          Connect to Database
        </button>
      </div>

      {/* Status banner */}
      {status.type !== STATUS.idle && (
        <div
          className="mt-4 p-4 rounded-lg text-center border"
          style={statusBannerStyle()}
        >
          {status.type === STATUS.loading && (
            <div className="loading mx-auto mb-2" />
          )}
          <div>{status.message}</div>
        </div>
      )}
    </div>
  );
}
