import { Routes, Route } from 'react-router-dom'
import Navbar     from './components/layout/Navbar'
import Home       from './pages/Home'
import ResumePage from './pages/Resume'
import InterviewPage from './pages/Interview'
import Dashboard  from './pages/Dashboard'
import { LoginPage, RegisterPage } from './pages/Auth'

export default function App() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <main style={{ flex: 1 }}>
        <Routes>
          <Route path="/"          element={<Home />} />
          <Route path="/resume"    element={<ResumePage />} />
          <Route path="/interview" element={<InterviewPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/login"     element={<LoginPage />} />
          <Route path="/register"  element={<RegisterPage />} />
          <Route path="*"          element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}

function NotFound() {
  return (
    <div style={{ textAlign: 'center', padding: '80px 20px' }}>
      <p style={{ fontSize: 64, marginBottom: 16 }}>404</p>
      <p style={{ color: '#94a3b8', marginBottom: 24 }}>Page not found</p>
      <a href="/" style={{ color: '#6366f1' }}>← Go Home</a>
    </div>
  )
}

function Footer() {
  return (
    <footer style={{ borderTop: '1px solid rgba(255,255,255,0.06)', padding: '20px', textAlign: 'center' }}>
      <p style={{ color: '#475569', fontSize: 13 }}>
        IntelliHire Pro v2.0 — AI-Powered Hiring Platform
      </p>
    </footer>
  )
}
