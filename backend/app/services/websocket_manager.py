from typing import Dict, List, Any
from fastapi import WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Active connections: {tenant_id: {user_id: [WebSocket]}}
        self.active_connections: Dict[int, Dict[int, List[WebSocket]]] = {}

    async def connect(self, websocket: WebSocket, tenant_id: int, user_id: int):
        await websocket.accept()
        
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = {}
        
        if user_id not in self.active_connections[tenant_id]:
            self.active_connections[tenant_id][user_id] = []
            
        self.active_connections[tenant_id][user_id].append(websocket)
        logger.info(f"WebSocket connected: User {user_id} in Tenant {tenant_id}")

    def disconnect(self, websocket: WebSocket, tenant_id: int, user_id: int):
        if tenant_id in self.active_connections and user_id in self.active_connections[tenant_id]:
            if websocket in self.active_connections[tenant_id][user_id]:
                self.active_connections[tenant_id][user_id].remove(websocket)
            
            if not self.active_connections[tenant_id][user_id]:
                del self.active_connections[tenant_id][user_id]
            
            if not self.active_connections[tenant_id]:
                del self.active_connections[tenant_id]
        
        logger.info(f"WebSocket disconnected: User {user_id} in Tenant {tenant_id}")

    async def send_personal_message(self, message: Any, user_id: int, tenant_id: int):
        if tenant_id in self.active_connections and user_id in self.active_connections[tenant_id]:
            for connection in self.active_connections[tenant_id][user_id]:
                await connection.send_json(message)

    async def broadcast_to_tenant(self, message: Any, tenant_id: int):
        if tenant_id in self.active_connections:
            for user_id in self.active_connections[tenant_id]:
                for connection in self.active_connections[tenant_id][user_id]:
                    await connection.send_json(message)

    async def broadcast_to_agents(self, message: Any, tenant_id: int, db: Any):
        # This would require checking user roles, better to handle via a tag or separate manager mapping
        # For MVP, we just broadcast to the whole tenant for simplicity, 
        # or implement a role-based connection mapping.
        await self.broadcast_to_tenant(message, tenant_id)

manager = ConnectionManager()
