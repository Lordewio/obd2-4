import asyncio
import json
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.job import Job

router = APIRouter()

# Store active WebSocket connections
active_connections: Dict[str, Set[WebSocket]] = {}

async def get_user_id(websocket: WebSocket) -> Optional[str]:
    try:
        # In production, get this from the auth token
        # For now, we'll just use a test user
        return "test_user"
    except:
        return None

@router.websocket("/ws/jobs")
async def websocket_endpoint(websocket: WebSocket, 
                           db: Session = Depends(get_db)):
    await websocket.accept()
    
    user_id = await get_user_id(websocket)
    if not user_id:
        await websocket.close()
        return
    
    # Add connection to active connections
    if user_id not in active_connections:
        active_connections[user_id] = set()
    active_connections[user_id].add(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message["type"] == "subscribe":
                job_id = message["job_id"]
                # Subscribe to job updates
                pass
            elif message["type"] == "update_status":
                job_id = message["job_id"]
                new_status = message["status"]
                # Update job status in database
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    job.status = new_status
                    db.commit()
                    # Notify all subscribers
                    await notify_job_update(job_id, new_status)
    except WebSocketDisconnect:
        # Remove connection when client disconnects
        active_connections[user_id].remove(websocket)
        if not active_connections[user_id]:
            del active_connections[user_id]

async def notify_job_update(job_id: str, status: str):
    """Notify all subscribers about job status update"""
    message = {
        "type": "job_update",
        "job_id": job_id,
        "status": status
    }
    
    # Send update to all connected clients
    for user_id, connections in active_connections.items():
        for connection in connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                # Remove disconnected client
                connections.remove(connection)
                if not connections:
                    del active_connections[user_id]
