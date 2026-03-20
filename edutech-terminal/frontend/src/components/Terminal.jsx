import React, { useEffect, useRef, useState } from 'react';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import 'xterm/css/xterm.css';

const TerminalComponent = ({ sessionId, onClose }) => {
  const terminalRef = useRef(null);
  const xtermRef = useRef(null);
  const wsRef = useRef(null);
  const fitAddonRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!terminalRef.current || !sessionId) return;

    // Initialize xterm.js
    const term = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
      theme: {
        background: '#1e1e1e',
        foreground: '#f0f0f0',
        cursor: '#00ff00',
        selection: '#ffffff40',
      },
      rows: 30,
      cols: 100,
    });

    // Add fit addon
    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    
    // Add web links addon
    term.loadAddon(new WebLinksAddon());

    // Open terminal
    term.open(terminalRef.current);
    fitAddon.fit();

    xtermRef.current = term;
    fitAddonRef.current = fitAddon;

    // Connect to WebSocket
    const wsUrl = `ws://localhost:8000/ws/terminal/${sessionId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      setError(null);
      term.writeln('Connected to terminal...');
    };

    ws.onmessage = (event) => {
      term.write(event.data);
    };

    ws.onerror = (error) => {
      setError('WebSocket connection error');
      term.writeln('\r\n\x1b[31mConnection error\x1b[0m');
    };

    ws.onclose = () => {
      setIsConnected(false);
      term.writeln('\r\n\x1b[33mConnection closed\x1b[0m');
    };

    // Handle terminal input
    term.onData((data) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(data);
      }
    });

    // Handle window resize
    const handleResize = () => {
      fitAddon.fit();
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      if (ws) {
        ws.close();
      }
      if (term) {
        term.dispose();
      }
    };
  }, [sessionId]);

  return (
    <div style={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      backgroundColor: '#1e1e1e'
    }}>
      {/* Terminal Header */}
      <div style={{
        padding: '10px 15px',
        backgroundColor: '#2d2d2d',
        color: '#fff',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        borderBottom: '1px solid #404040'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: isConnected ? '#00ff00' : '#ff0000'
          }} />
          <span>Terminal {sessionId.slice(0, 8)}</span>
          {error && <span style={{ color: '#ff6b6b', fontSize: '12px' }}>{error}</span>}
        </div>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            color: '#fff',
            cursor: 'pointer',
            fontSize: '18px',
            padding: '0 5px'
          }}
        >
          ✕
        </button>
      </div>

      {/* Terminal */}
      <div 
        ref={terminalRef} 
        style={{ 
          flex: 1, 
          padding: '10px',
          overflow: 'hidden'
        }} 
      />
    </div>
  );
};

export default TerminalComponent;