import { useState, useEffect, useRef } from 'react';

const useWebSocket = (tableId, onMessageCallback) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState(null);
  const webSocketRef = useRef(null);

  useEffect(() => {
    if (!tableId) {
      if (webSocketRef.current) {
        // console.log(`WebSocket: Closing connection for table ${webSocketRef.current.tableId}`);
        webSocketRef.current.close();
        webSocketRef.current = null;
      }
      setIsConnected(false);
      return;
    }

    // Close existing connection if tableId changes
    if (webSocketRef.current && webSocketRef.current.tableId !== tableId) {
        // console.log(`WebSocket: Closing old connection for table ${webSocketRef.current.tableId} due to new table ${tableId}`);
        webSocketRef.current.close();
        webSocketRef.current = null;
    }
    
    // Connect only if there's no current connection or if it's for a different table
    if (!webSocketRef.current) {
        const wsUrl = `ws://localhost:8000/ws/table/${tableId}`; // Ensure this matches your backend URL/port
        // console.log(`WebSocket: Attempting to connect to ${wsUrl}`);
        const ws = new WebSocket(wsUrl);
        ws.tableId = tableId; // Store tableId for comparison on change

        ws.onopen = () => {
          // console.log(`WebSocket: Connected to table ${tableId}`);
          setIsConnected(true);
          setError(null);
        };

        ws.onmessage = (event) => {
          try {
            const messageData = JSON.parse(event.data);
            setLastMessage(messageData); // Store raw message if needed
            if (onMessageCallback) {
              onMessageCallback(messageData); // Pass to store handler
            }
          } catch (e) {
            console.error('WebSocket: Error parsing message JSON:', e);
          }
        };

        ws.onerror = (event) => {
          console.error('WebSocket: Error:', event);
          setError('WebSocket error occurred. Check console.');
          // setIsConnected(false); // Consider if an error should immediately set to not connected
        };

        ws.onclose = (event) => {
          // console.log(`WebSocket: Disconnected from table ${tableId}. Clean disconnect: ${event.wasClean}, Code: ${event.code}, Reason: ${event.reason}`);
          setIsConnected(false);
          // Avoid auto-reconnect for this basic setup, but could be added here.
          // If it was the current connection that closed, nullify ref
          if (webSocketRef.current && webSocketRef.current.tableId === tableId) {
            webSocketRef.current = null;
          }
        };
        
        webSocketRef.current = ws;
    }

    // Cleanup function for when the component unmounts or tableId changes
    return () => {
      if (webSocketRef.current && webSocketRef.current.tableId === tableId) {
        // console.log(`WebSocket: Cleanup - Closing connection for table ${tableId}`);
        webSocketRef.current.close();
        webSocketRef.current = null;
        setIsConnected(false);
      }
    };
  }, [tableId, onMessageCallback]); // Dependency array ensures effect runs when tableId or callback changes

  return { isConnected, lastMessage, error };
};

export default useWebSocket;
