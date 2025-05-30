from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from ..websocket_manager import ConnectionManager, get_connection_manager

router = APIRouter(
    tags=["websockets"],
)

@router.websocket("/ws/table/{table_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    table_id: str,
    manager: ConnectionManager = Depends(get_connection_manager)
):
    room_id = f"table_{table_id}"
    await manager.connect(websocket, room_id)
    try:
        while True:
            # Keep the connection alive by waiting for messages.
            # If you need to handle client-sent messages, process them here.
            # For now, this primarily serves to keep the connection open for server-sent events.
            data = await websocket.receive_text()
            # Optionally, echo back or handle client messages:
            # await manager.broadcast_to_room(f"Client {websocket.client} in room {room_id} says: {data}", room_id)
            print(f"Received message from {websocket.client} in room {room_id}: {data} (not broadcasting)")
    except WebSocketDisconnect:
        print(f"WebSocket {websocket.client} in room {room_id} disconnected (WebSocketDisconnect exception).")
        manager.disconnect(websocket, room_id)
    except Exception as e:
        # Catch other exceptions that might occur during receive_text or other operations
        print(f"An error occurred with WebSocket {websocket.client} in room {room_id}: {e}")
        manager.disconnect(websocket, room_id) # Ensure disconnect on other errors too
    finally:
        # This block might not always be reached if disconnect happens abruptly.
        # The disconnect logic in ConnectionManager should be robust to handle removals.
        print(f"WebSocket connection for {websocket.client} in room {room_id} is closing (finally block).")
        # Ensure disconnect is called if not already by an exception handler
        # This check avoids calling disconnect twice if already handled by WebSocketDisconnect
        if room_id in manager.active_connections and websocket in manager.active_connections[room_id]:
             manager.disconnect(websocket, room_id)
