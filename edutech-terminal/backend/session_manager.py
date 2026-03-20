"""
Session management for terminal sessions
"""

import asyncio
import uuid
import time
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

SESSION_TIMEOUT_SECONDS = 3600  # 1 hour

class SessionManager:
    """Manage terminal sessions and container lifecycle"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.timeout = SESSION_TIMEOUT_SECONDS
    
    async def create_session(self, user_id: str, environment_type: str = "ubuntu") -> str:
        """Create new terminal session and spawn container"""
        session_id = str(uuid.uuid4())
        pod_name = f"terminal-{user_id[:8]}-{session_id[:8]}"
        
        # In production, this would call Kubernetes API to spawn pod
        await self._spawn_container(pod_name, environment_type)
        
        session = {
            "id": session_id,
            "user_id": user_id,
            "pod_name": pod_name,
            "created_at": time.time(),
            "last_activity": time.time(),
            "status": "active",
            "environment_type": environment_type
        }
        
        self.active_sessions[session_id] = session
        
        # Import here to avoid circular dependency
        from main import sessions_db
        sessions_db[session_id] = session
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id
    
    async def _spawn_container(self, pod_name: str, environment_type: str):
        """Spawn container/pod for terminal (mock implementation)"""
        # In production, use Kubernetes Python client:
        # from kubernetes import client, config
        # v1 = client.CoreV1Api()
        # pod = v1.create_namespaced_pod(namespace="terminals", body=pod_manifest)
        
        logger.info(f"Spawning container: {pod_name} with type: {environment_type}")
        await asyncio.sleep(0.1)  # Simulate container startup
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        return self.active_sessions.get(session_id)
    
    async def update_activity(self, session_id: str):
        """Update last activity timestamp"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["last_activity"] = time.time()
    
    async def terminate_session(self, session_id: str):
        """Terminate session and cleanup container"""
        session = self.active_sessions.get(session_id)
        if session:
            await self._cleanup_container(session["pod_name"])
            session["status"] = "terminated"
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            logger.info(f"Terminated session {session_id}")
    
    async def _cleanup_container(self, pod_name: str):
        """Delete container/pod (mock implementation)"""
        # In production: v1.delete_namespaced_pod(name=pod_name, namespace="terminals")
        logger.info(f"Cleaning up container: {pod_name}")
        await asyncio.sleep(0.1)
    
    async def cleanup_inactive_sessions(self):
        """Background task to cleanup inactive sessions"""
        while True:
            now = time.time()
            inactive = []
            
            for session_id, session in list(self.active_sessions.items()):
                if now - session["last_activity"] > self.timeout:
                    inactive.append(session_id)
            
            for session_id in inactive:
                await self.terminate_session(session_id)
            
            await asyncio.sleep(60)  # Check every minute