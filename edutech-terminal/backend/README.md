# EduTech Terminal Platform - Backend

FastAPI-based backend with WebSocket support for interactive terminal sessions.

## 📁 Project Structure

```
backend/
├── main.py                  # FastAPI application entry point
├── models.py                # Pydantic models for validation
├── session_manager.py       # Session lifecycle management
├── websocket_handler.py     # WebSocket terminal I/O handler
├── k8s_manager.py          # Kubernetes pod manager (production)
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container image definition
├── .env                   # Environment variables
└── README.md              # This file
```

## 🚀 Quick Start

### Option 1: Local Development (Without Kubernetes)

```bash
# 1. Create virtual environment
python -m venv venv
#python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env
# Edit .env with your configuration

# 4. Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 5. Access API docs
# http://localhost:8000/docs
```

### Option 2: Docker

```bash
# Build image
docker build -t edutech-backend .

# Run container
docker run -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  edutech-backend

# Or use docker-compose (from root directory)
cd ..
docker-compose up backend
```

### Option 3: Production (Kubernetes)

```bash
# Ensure kubectl is configured
kubectl config current-context

# Deploy backend
kubectl apply -f ../k8s/backend-deployment.yaml

# Check status
kubectl get pods -n edutech-terminal
kubectl logs -f deployment/backend-deployment -n edutech-terminal
```

## 📋 File Descriptions

### **main.py**
- FastAPI application setup
- API endpoints (auth, courses, sessions)
- WebSocket endpoint for terminal
- Startup/shutdown event handlers
- Demo user creation

### **models.py**
- Pydantic models for request/response validation
- User, Course, Session, Lab models
- Type safety and automatic documentation

### **session_manager.py**
- Terminal session lifecycle management
- Container spawning (mock in dev, real in production)
- Session timeout handling
- Background cleanup tasks

### **websocket_handler.py**
- WebSocket connection management
- Bidirectional terminal I/O
- Command simulation (dev mode)
- Real container exec (production)

### **k8s_manager.py**
- Kubernetes pod management
- Pod creation with security contexts
- Resource limits and quotas
- Exec stream handling
- Pod cleanup

### **config.py**
- Environment-based configuration
- Settings validation with Pydantic
- Cached configuration loading

## 🔧 Configuration

### Environment Variables

```bash
# Security
SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET=your-jwt-secret-key-change-in-production

# Database (optional, defaults to SQLite)
DATABASE_URL=postgresql://user:pass@localhost:5432/edutech

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Kubernetes
KUBERNETES_NAMESPACE=edutech-terminal
USE_KUBERNETES=false  # Set to true in production

# Session
SESSION_TIMEOUT=3600  # 1 hour

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

## 🔐 API Endpoints

### Authentication
- `POST /signup` - User registration
- `POST /token` - User login (OAuth2 password flow)
- `GET /me` - Get current user info

### Courses
- `GET /courses` - List all courses
- `GET /courses/{course_id}` - Get course details

### Sessions
- `POST /sessions/create?environment_type=ubuntu` - Create terminal session
- `GET /sessions` - List user's active sessions
- `DELETE /sessions/{session_id}` - Terminate session

### WebSocket
- `WS /ws/terminal/{session_id}` - Terminal I/O stream

### Health
- `GET /health` - Health check endpoint

## 📊 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🧪 Testing

### Manual Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demo123"

# Create session (with token)
curl -X POST http://localhost:8000/sessions/create?environment_type=ubuntu \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### WebSocket Testing

```python
import asyncio
import websockets

async def test_terminal():
    uri = "ws://localhost:8000/ws/terminal/SESSION_ID"
    async with websockets.connect(uri) as websocket:
        # Send command
        await websocket.send("ls\n")
        
        # Receive output
        response = await websocket.recv()
        print(response)

asyncio.run(test_terminal())
```

## 🔒 Security Features

### Authentication
- JWT tokens with expiration
- Bcrypt password hashing
- OAuth2 password flow
- Protected endpoints with dependency injection

### Container Security
- Non-root user execution (UID 1000)
- No privilege escalation
- Capabilities dropped
- Resource limits enforced
- Network policies (in Kubernetes)
- Readonly root filesystem where possible

### Session Security
- Session timeout (1 hour default)
- User isolation (separate containers)
- Automatic cleanup of inactive sessions

## 📈 Monitoring

### Metrics Endpoint
```python
# Add to main.py for production
from prometheus_client import Counter, Histogram, make_asgi_app

# Metrics
terminal_sessions = Counter('terminal_sessions_total', 'Total terminal sessions')
session_duration = Histogram('session_duration_seconds', 'Session duration')

# Mount metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

### Logging
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
# Kill it
kill -9 PID
```

### Module Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Kubernetes Connection Failed
```bash
# Check kubectl config
kubectl config current-context
kubectl get nodes

# Verify namespace exists
kubectl get namespace edutech-terminal
```

### WebSocket Connection Refused
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check CORS settings in main.py
# Ensure frontend origin is allowed
```

## 🚀 Production Deployment

### Environment Setup
```bash
# 1. Set production environment variables
export SECRET_KEY=$(openssl rand -hex 32)
export JWT_SECRET=$(openssl rand -hex 32)
export DATABASE_URL=postgresql://user:pass@db:5432/edutech
export USE_KUBERNETES=true

# 2. Run database migrations (if using SQLAlchemy)
alembic upgrade head

# 3. Deploy to Kubernetes
kubectl apply -f ../k8s/
```

### Production Checklist
- [ ] Set strong SECRET_KEY and JWT_SECRET
- [ ] Configure production database (PostgreSQL)
- [ ] Set up Redis for session storage
- [ ] Enable Kubernetes integration
- [ ] Configure resource limits
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Enable SSL/TLS
- [ ] Configure backup strategy
- [ ] Set up logging aggregation
- [ ] Configure alerts

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Kubernetes Python Client](https://github.com/kubernetes-client/python)
- [WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)
- [JWT Authentication](https://jwt.io)

## 🤝 Development Tips

1. **Use reload mode** during development:
   ```bash
   uvicorn main:app --reload
   ```

2. **Check logs** for errors:
   ```bash
   tail -f logs/app.log
   ```

3. **Test WebSocket** connections:
   - Use browser DevTools Network tab
   - Use wscat: `wscat -c ws://localhost:8000/ws/terminal/SESSION_ID`

4. **Debug mode**:
   ```python
   # Add to main.py
   import debugpy
   debugpy.listen(("0.0.0.0", 5678))
   ```

---

**Ready to go!** Start the backend and connect the frontend for a complete interactive terminal experience.