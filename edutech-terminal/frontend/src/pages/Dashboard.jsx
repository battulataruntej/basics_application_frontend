import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { courseAPI, sessionAPI } from '../api/client';
import TerminalComponent from '../components/Terminal';

const Dashboard = () => {
  const { user, logout } = useAuthStore();
  const [courses, setCourses] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadCourses();
    loadSessions();
  }, []);

  const loadCourses = async () => {
    try {
      const data = await courseAPI.getCourses();
      setCourses(data);
    } catch (error) {
      console.error('Failed to load courses:', error);
    }
  };

  const loadSessions = async () => {
    try {
      const data = await sessionAPI.getSessions();
      setSessions(data);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const handleCreateSession = async (environmentType = 'ubuntu') => {
    setLoading(true);
    try {
      const session = await sessionAPI.createSession(environmentType);
      setActiveSessionId(session.session_id);
      await loadSessions();
    } catch (error) {
      console.error('Failed to create session:', error);
      alert('Failed to create terminal session');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseTerminal = async () => {
    if (activeSessionId) {
      try {
        await sessionAPI.deleteSession(activeSessionId);
      } catch (error) {
        console.error('Failed to delete session:', error);
      }
      setActiveSessionId(null);
      await loadSessions();
    }
  };

  if (activeSessionId) {
    return (
      <div style={{ height: '100vh', overflow: 'hidden' }}>
        <TerminalComponent 
          sessionId={activeSessionId} 
          onClose={handleCloseTerminal}
        />
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* Header */}
      <header style={{
        backgroundColor: '#fff',
        padding: '15px 30px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <h1 style={{ margin: 0, color: '#333' }}>EduTech Terminal</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <span style={{ color: '#666' }}>Welcome, {user?.username}!</span>
          <button
            onClick={logout}
            style={{
              padding: '8px 16px',
              backgroundColor: '#fff',
              border: '1px solid #ddd',
              borderRadius: '5px',
              cursor: 'pointer',
            }}
          >
            Logout
          </button>
        </div>
      </header>

      <div style={{ padding: '30px', maxWidth: '1200px', margin: '0 auto' }}>
        {/* Quick Actions */}
        <section style={{ marginBottom: '40px' }}>
          <h2 style={{ marginBottom: '20px', color: '#333' }}>Quick Start</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
            <button
              onClick={() => handleCreateSession('ubuntu')}
              disabled={loading}
              style={{
                padding: '20px',
                backgroundColor: '#667eea',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: '16px',
                fontWeight: '600',
              }}
            >
              🐧 Ubuntu Terminal
            </button>
            <button
              onClick={() => handleCreateSession('docker')}
              disabled={loading}
              style={{
                padding: '20px',
                backgroundColor: '#4c9aff',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: '16px',
                fontWeight: '600',
              }}
            >
              🐳 Docker Environment
            </button>
            <button
              onClick={() => handleCreateSession('kubernetes')}
              disabled={loading}
              style={{
                padding: '20px',
                backgroundColor: '#326ce5',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: '16px',
                fontWeight: '600',
              }}
            >
              ☸️ Kubernetes Lab
            </button>
          </div>
        </section>

        {/* Available Courses */}
        <section style={{ marginBottom: '40px' }}>
          <h2 style={{ marginBottom: '20px', color: '#333' }}>Available Courses</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
            {courses.map((course) => (
              <div
                key={course.id}
                style={{
                  backgroundColor: '#fff',
                  padding: '20px',
                  borderRadius: '8px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                }}
              >
                <h3 style={{ marginTop: 0, color: '#333' }}>{course.title}</h3>
                <p style={{ color: '#666', fontSize: '14px' }}>{course.description}</p>
                <div style={{ 
                  display: 'inline-block',
                  padding: '5px 10px',
                  backgroundColor: course.difficulty === 'beginner' ? '#e8f5e9' : '#fff3e0',
                  color: course.difficulty === 'beginner' ? '#2e7d32' : '#e65100',
                  borderRadius: '5px',
                  fontSize: '12px',
                  fontWeight: '600',
                  marginTop: '10px',
                }}>
                  {course.difficulty}
                </div>
                <div style={{ marginTop: '10px', color: '#666', fontSize: '13px' }}>
                  {course.labs.length} labs available
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Active Sessions */}
        {sessions.length > 0 && (
          <section>
            <h2 style={{ marginBottom: '20px', color: '#333' }}>Active Sessions</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {sessions.map((session) => (
                <div
                  key={session.id}
                  style={{
                    backgroundColor: '#fff',
                    padding: '15px',
                    borderRadius: '8px',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <div>
                    <div style={{ fontWeight: '600', color: '#333' }}>
                      Session {session.id.slice(0, 8)}
                    </div>
                    <div style={{ fontSize: '13px', color: '#666' }}>
                      Environment: {session.environment_type}
                    </div>
                  </div>
                  <button
                    onClick={() => setActiveSessionId(session.id)}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#667eea',
                      color: '#fff',
                      border: 'none',
                      borderRadius: '5px',
                      cursor: 'pointer',
                    }}
                  >
                    Connect
                  </button>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
};

export default Dashboard;