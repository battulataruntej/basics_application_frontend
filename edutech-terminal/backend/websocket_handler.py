"""
WebSocket handler for terminal I/O
"""

import asyncio
import logging
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)

class TerminalConnection:
    """Handle WebSocket connection to terminal"""
    
    def __init__(self, websocket: WebSocket, session_id: str):
        self.websocket = websocket
        self.session_id = session_id
        self.running = False
    
    async def connect(self):
        """Accept WebSocket connection"""
        await self.websocket.accept()
        logger.info(f"WebSocket connected for session {self.session_id}")
    
    async def handle_terminal_io(self):
        """Handle bidirectional terminal I/O"""
        self.running = True
        
        # Create tasks for input and output
        input_task = asyncio.create_task(self._handle_input())
        output_task = asyncio.create_task(self._handle_output())
        
        try:
            await asyncio.gather(input_task, output_task)
        except Exception as e:
            logger.error(f"Terminal I/O error: {e}")
        finally:
            self.running = False
    
    async def _handle_input(self):
        """Forward user input to container"""
        try:
            # Import here to avoid circular dependency
            from session_manager import SessionManager
            session_manager = SessionManager()
            
            while self.running:
                # Receive from WebSocket
                data = await self.websocket.receive_text()
                
                # Update session activity
                await session_manager.update_activity(self.session_id)
                
                # In production, send to container stdin via Kubernetes exec
                # For demo, echo back with prompt
                await self._send_to_container(data)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for session {self.session_id}")
            self.running = False
    
    async def _handle_output(self):
        """Forward container output to WebSocket"""
        try:
            # In production, read from container stdout
            # For demo, simulate terminal responses
            await self.websocket.send_text("\r\n\033[1;32mWelcome to EduTech Terminal!\033[0m\r\n")
            await self.websocket.send_text("learner@edutech:~$ ")
            
            while self.running:
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Output handling error: {e}")
            self.running = False
    
    async def _send_to_container(self, command: str):
        """Send command to container (mock implementation)"""
        # In production: use kubernetes.stream.stream() to execute commands
        
        # Simulate command execution
        response = self._simulate_command(command.strip())
        await self.websocket.send_text(f"\r\n{response}\r\nlearner@edutech:~$ ")
    
    def _simulate_command(self, command: str) -> str:
        """Simulate basic shell commands for demo"""
        if command == "ls":
            return "Documents  Downloads  Pictures  projects  README.md"
        elif command == "pwd":
            return "/home/learner"
        elif command.startswith("echo"):
            return command[5:]
        elif command == "whoami":
            return "learner"
        elif command == "date":
            return datetime.now().strftime("%a %b %d %H:%M:%S UTC %Y")
        elif command == "help":
            return "Available commands: ls, pwd, echo, whoami, date, help, clear"
        elif command == "clear":
            return "\033[2J\033[H"
        elif command == "uname -a":
            return "Linux edutech 5.15.0-1023-aws #27-Ubuntu SMP x86_64 GNU/Linux"
        elif command.startswith("mkdir"):
            return ""
        elif command.startswith("touch"):
            return ""
        elif command.startswith("cd"):
            return ""
        else:
            return f"bash: {command}: command not found"