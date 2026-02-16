import { useState } from 'react';
import Background from './components/Background';
import Header from './components/Header';
import UploadScreen from './components/UploadScreen';
import ChatScreen from './components/ChatScreen';

export default function App() {
  const [session, setSession] = useState(null);

  function handleSessionReady(sessionId, sourceName) {
    setSession({ id: sessionId, sourceName });
  }

  function handleReset() {
    setSession(null);
  }

  return (
    <>
      <Background />

      <div className="container">
        <Header />

        {!session ? (
          <UploadScreen onSessionReady={handleSessionReady} />
        ) : (
          <ChatScreen
            sessionId={session.id}
            sourceName={session.sourceName}
            onReset={handleReset}
          />
        )}
      </div>
    </>
  );
}
