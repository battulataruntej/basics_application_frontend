# EduTech Terminal Platform - AI Coding Agent Instructions

## Architecture Overview

**EduTech Terminal** is a full-stack educational platform enabling interactive Linux terminal sessions in the browser. The system uses a **FastAPI backend** with **WebSocket support** and a **React frontend** with xterm.js for terminal emulation.

### Key Architecture Decisions
- **WebSocket for real-time terminal I/O**: Bidirectional communication for command execution and output streaming
- **Session-based lifecycle**: Each terminal session = one spawned container with timeout cleanup
- **OAuth2 + JWT authentication**: Stateless token-based auth with Bearer tokens in headers
- **In-memory databases in dev mode**: Replace with PostgreSQL in production (see `docker-compose.yml`)
- **Kubernetes-ready deployment**: All services containerized; `deploy.sh` orchestrates K8s manifests

## Project Structure & File Responsibilities

### Backend (FastAPI)
- `main.py`: Entry point—FastAPI app setup, endpoints (auth, courses, sessions), WebSocket routes, demo data
- `models.py`: Pydantic models—User, Course, Session, Lab definitions with validation
- `websocket_handler.py`: WebSocket connection class—handles terminal I/O, input/output tasks
- `session_manager.py`: Session lifecycle—container spawning (mock in dev), timeouts, cleanup tasks
- `k8s_manager.py`: Kubernetes integration—pod creation/deletion via kubectl API
- `config.py`: Configuration management—environment variables, defaults

### Frontend (React)
- `src/App.js`: Main component—routing, page layout, auth guard
- `src/api/client.js`: Axios client—request interceptor adds Bearer token, response interceptor handles 401
- `src/store/authStore.js`: Zustand state—manages user, token, login/logout
- `src/components/Terminal.jsx`: xterm.js wrapper—WebSocket connection, command execution
- `src/pages/Login.jsx`: Auth UI—signup/login forms
- `src/pages/Dashboard.jsx`: Main UI—course list, lab selection, terminal launch

## Data Flow & Integration Points

### Authentication Flow
1. User submits credentials to **POST /token** (OAuth2 PasswordRequestForm)
2. Backend validates, returns JWT token (HS256, 60-min expiry)
3. Frontend stores token in localStorage, includes in all API requests via `Authorization: Bearer <token>`
4. Backend validates token on protected endpoints with `jwt.decode()` and custom `get_current_user()` dependency

### Terminal Session Lifecycle
1. User clicks "Start Lab" → **POST /sessions** with lab_id
2. Backend creates TerminalSession record, spawns container via SessionManager
3. Frontend receives session_id, establishes **WebSocket /ws/{session_id}**
4. TerminalConnection handles bidirectional I/O:
   - **_handle_input()**: WebSocket → container stdin
   - **_handle_output()**: container stdout → WebSocket
5. User closes session or timeout occurs → cleanup task removes container

## Critical Developer Workflows

### Local Development (No Docker)
```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
cd frontend
npm install && npm start  # Opens http://localhost:3000
```

### Docker Compose (Full Stack)
```bash
docker-compose up  # Starts backend, frontend, postgres, redis
# Backend: http://localhost:8000/docs
# Frontend: http://localhost:3000
```

### Kubernetes Deployment
```bash
./deploy.sh  # Applies all K8s manifests in k8s/ directory
kubectl get pods -n edutech-terminal
```

### Database Setup
- **Development**: In-memory dict (users_db, sessions_db) in `backend/main.py`
- **Production**: PostgreSQL via SQLAlchemy ORM (see `docker-compose.yml`)
- **Caching**: Redis for session caching (optional, configured in env)

## Conventions & Patterns

### Error Handling
- **Backend**: Raise HTTPException with status codes, logged with timestamps
- **Frontend**: authStore.js auto-redirects on 401; axios catches errors, displays user feedback
- **WebSocket**: Catch WebSocketDisconnect, log error, cleanup session resources

### Async Patterns
- **Backend**: All WebSocket handlers are async; use asyncio.create_task() for concurrent input/output
- **Frontend**: Zustand actions use async/await; axios promises handled via .then/.catch

### State Management
- **Frontend**: Zustand (authStore.js)—single source of truth for user, token, auth state
- **Backend**: In-memory dicts for dev; ORM models for production

### Environment Configuration
- **Backend**: python-dotenv loads .env; SECRET_KEY, DATABASE_URL, REDIS_URL
- **Frontend**: REACT_APP_API_URL, REACT_APP_WS_URL from .env (CRA auto-prefixes REACT_APP_)

## Key Dependencies & Integrations

### Backend Dependencies
- **FastAPI**: Web framework with auto-generated OpenAPI docs
- **uvicorn**: ASGI server (use --reload for dev auto-restart)
- **pydantic**: Schema validation, automatic error responses
- **python-jose**: JWT encoding/decoding for auth tokens
- **websockets**: Low-level WebSocket protocol (wrapped by FastAPI)
- **kubernetes**: Python client for pod management in K8s
- **sqlalchemy + alembic**: ORM + migrations (production database)

### Frontend Dependencies
- **React 18**: UI framework with hooks
- **xterm.js**: Terminal emulator (see Terminal.jsx for integration pattern)
- **axios**: HTTP client with interceptor support
- **zustand**: Lightweight state management (no Redux complexity)
- **react-router-dom**: Client-side routing

## Important Gotchas & Practices

1. **WebSocket auth**: Token passed in query param or header during handshake; validate before accepting connection
2. **Session cleanup**: SessionManager must remove containers on timeout; background task runs periodically
3. **CORS config**: `backend/main.py` hardcodes localhost:3000/3001—update for production
4. **Token expiry**: 60 minutes by default; frontend must refresh token or re-authenticate
5. **Frontend env vars**: REACT_APP_ prefix required for CRA; not available in build without rebuild
6. **Container spawning**: Dev mode uses mock (subprocess), production uses K8s API—toggle via config
7. **xterm.js sizing**: Call terminal.fit() on container resize; see Terminal.jsx for example
8. **Demo data**: courses_db seeded in main.py startup—remove or connect to real database

## When Adding Features

- **New API endpoint**: Add model in models.py, endpoint in main.py, client method in src/api/client.js
- **New page**: Create in src/pages/, add route in App.js, update navigation
- **WebSocket change**: Modify both websocket_handler.py and Terminal.jsx; test real-time communication
- **Database schema change**: Update models.py (Pydantic + SQLAlchemy ORM), create migration with alembic
- **New service**: Add container in docker-compose.yml, update depends_on relationships

