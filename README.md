# EduTech Terminal - Frontend Setup Guide

## 📁 Project Structure

Create the following folder structure:

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── api/
│   │   └── client.js
│   ├── components/
│   │   └── Terminal.jsx
│   ├── pages/
│   │   ├── Login.jsx
│   │   └── Dashboard.jsx
│   ├── store/
│   │   └── authStore.js
│   ├── App.js
│   ├── index.js
│   └── index.css
├── .env
├── package.json
└── README.md
```

## 🚀 Quick Start

### Step 1: Create React App

```bash
# Create the frontend directory
mkdir frontend
cd frontend

# Initialize npm (if not already done)
npm init -y
```

### Step 2: Install Dependencies

Copy the `package.json` file I provided, then run:

```bash
npm install
```

This will install:
- **react** & **react-dom**: Core React library
- **react-router-dom**: Client-side routing
- **xterm**: Terminal emulator
- **xterm-addon-fit**: Auto-sizing for terminal
- **xterm-addon-web-links**: Clickable links in terminal
- **axios**: HTTP client for API calls
- **zustand**: State management
- **react-scripts**: Build tooling

### Step 3: Copy All Files

Copy each file I created into the correct location:

1. **package.json** → `frontend/package.json`
2. **public/index.html** → `frontend/public/index.html`
3. **src/index.js** → `frontend/src/index.js`
4. **src/index.css** → `frontend/src/index.css`
5. **src/App.js** → `frontend/src/App.js`
6. **src/api/client.js** → `frontend/src/api/client.js`
7. **src/store/authStore.js** → `frontend/src/store/authStore.js`
8. **src/components/Terminal.jsx** → `frontend/src/components/Terminal.jsx`
9. **src/pages/Login.jsx** → `frontend/src/pages/Login.jsx`
10. **src/pages/Dashboard.jsx** → `frontend/src/pages/Dashboard.jsx`
11. **.env** → `frontend/.env`

### Step 4: Start Development Server

```bash
npm start
```

The app will open at **http://localhost:3000**

## 🔧 Configuration

### Environment Variables (.env)

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

**For Production:**
```env
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_WS_URL=wss://api.yourdomain.com
```

## 📦 Building for Production

```bash
# Create optimized production build
npm run build

# The build folder will contain static files ready to deploy
```

## 🐳 Docker Build

If you want to containerize the frontend:

```bash
# Build Docker image
docker build -t edutech-frontend .

# Run container
docker run -p 3000:80 edutech-frontend
```

## 🧪 Testing

```bash
npm test
```

## 📝 File Descriptions

### **src/api/client.js**
- Axios configuration with interceptors
- API endpoints for auth, courses, sessions
- Automatic token handling
- Error handling and redirects

### **src/store/authStore.js**
- Zustand state management
- Login/signup/logout logic
- JWT token storage
- Authentication state

### **src/components/Terminal.jsx**
- xterm.js terminal component
- WebSocket connection handler
- Terminal I/O bidirectional streaming
- Connection status indicator

### **src/pages/Login.jsx**
- Login/signup form
- Form validation
- Error display
- Demo credentials display

### **src/pages/Dashboard.jsx**
- Course listing
- Session management
- Quick launch buttons
- Active sessions display

### **src/App.js**
- React Router setup
- Protected routes
- Authentication check on mount

## 🎨 Features

### Authentication
- JWT-based authentication
- Persistent sessions with localStorage
- Auto-redirect on token expiry
- Login/signup toggle

### Terminal
- Full xterm.js terminal emulator
- WebSocket real-time communication
- Auto-resize on window changes
- Clickable links support
- Connection status indicator

### Dashboard
- Quick launch terminals (Ubuntu, Docker, Kubernetes)
- Browse available courses
- Manage active sessions
- Connect to existing sessions

## 🔒 Security Features

- JWT token storage in localStorage
- Automatic token injection in API calls
- 401 handling with auto-logout
- Protected routes with authentication check

## 🌐 API Integration

The frontend connects to these backend endpoints:

**Authentication:**
- `POST /signup` - User registration
- `POST /token` - User login
- `GET /me` - Get current user

**Courses:**
- `GET /courses` - List all courses
- `GET /courses/{id}` - Get course details

**Sessions:**
- `POST /sessions/create` - Create terminal session
- `GET /sessions` - List user sessions
- `DELETE /sessions/{id}` - Terminate session

**WebSocket:**
- `WS /ws/terminal/{session_id}` - Terminal I/O stream

## 🎯 Demo Credentials

Default demo account (if backend is running):
- **Username:** demo
- **Password:** demo123

## 🛠️ Troubleshooting

### WebSocket Connection Failed
```
Error: WebSocket connection to 'ws://localhost:8000' failed
```
**Solution:** Make sure the backend is running on port 8000

### CORS Error
```
Access to XMLHttpRequest blocked by CORS policy
```
**Solution:** Backend must have CORS enabled for `http://localhost:3000`

### Module Not Found
```
Cannot find module 'xterm'
```
**Solution:** Run `npm install` to install all dependencies

### Port Already in Use
```
Something is already running on port 3000
```
**Solution:** Kill the process or use a different port:
```bash
PORT=3001 npm start
```

## 📚 Additional Resources

- [React Documentation](https://react.dev)
- [xterm.js Documentation](https://xtermjs.org)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [React Router Documentation](https://reactrouter.com)

## 🚀 Next Steps

1. **Start Backend:** Make sure the FastAPI backend is running
2. **Start Frontend:** Run `npm start` in the frontend directory
3. **Open Browser:** Navigate to http://localhost:3000
4. **Login:** Use demo/demo123 or create a new account
5. **Launch Terminal:** Click "Ubuntu Terminal" to start

## 💡 Development Tips

- **Hot Reload:** Changes auto-reload in development
- **Console Errors:** Check browser console for errors
- **Network Tab:** Monitor API calls in DevTools
- **React DevTools:** Install for component debugging
- **Terminal Input:** Click inside terminal to focus

## 🎨 Customization

### Change Theme Colors
Edit the gradient in `Login.jsx`:
```javascript
background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
```

### Modify Terminal Theme
Edit theme in `Terminal.jsx`:
```javascript
theme: {
  background: '#1e1e1e',
  foreground: '#f0f0f0',
  cursor: '#00ff00',
}
```

### Add New Environment Types
Add buttons in `Dashboard.jsx`:
```javascript
<button onClick={() => handleCreateSession('python')}>
  🐍 Python Environment
</button>
```

---

**Need Help?** Check the backend logs and browser console for error details.

**Ready to Deploy?** See the main README.md for Kubernetes deployment instructions.