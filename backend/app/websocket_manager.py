from fastapi import WebSocket
from typing import List, Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)
        print(f"WebSocket {websocket.client} connected to room {room_id}. Total clients in room: {len(self.active_connections[room_id])}")


    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)
                print(f"WebSocket {websocket.client} disconnected from room {room_id}. Total clients in room: {len(self.active_connections[room_id])}")
                if not self.active_connections[room_id]: # Remove room if empty
                    del self.active_connections[room_id]
                    print(f"Room {room_id} removed as it is empty.")
            else:
                print(f"Warning: WebSocket {websocket.client} not found in room {room_id} during disconnect.")
        else:
            print(f"Warning: Room {room_id} not found during disconnect for WebSocket {websocket.client}.")


    async def broadcast_to_room(self, message: str, room_id: str):
        if room_id in self.active_connections:
            disconnected_clients = []
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_text(message)
                except Exception as e: # Catches various errors including WebSocketDisconnect, ConnectionClosed
                    print(f"Error sending message to {connection.client} in room {room_id}: {e}. Marking for disconnect.")
                    disconnected_clients.append(connection)
            
            # Clean up disconnected clients after broadcast attempt
            for client_to_disconnect in disconnected_clients:
                self.disconnect(client_to_disconnect, room_id)


    async def broadcast_json_to_room(self, data: dict, room_id: str):
        if room_id in self.active_connections:
            disconnected_clients = []
            # Convert dict to JSON string for sending
            import json # Local import
            message = json.dumps(data) 
            
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_text(message) # send_text expects string
                except Exception as e:
                    print(f"Error sending JSON message to {connection.client} in room {room_id}: {e}. Marking for disconnect.")
                    disconnected_clients.append(connection)

            for client_to_disconnect in disconnected_clients:
                self.disconnect(client_to_disconnect, room_id)

# Global instance (or use FastAPI dependency injection for a singleton)
manager = ConnectionManager()

def get_connection_manager():
    return manager
