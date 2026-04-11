import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Brain, FileText, Mic, BarChart3, LogOut, LogIn, Menu, X } from 'lucide-react'
import { useState } from 'react'
import { useAuthStore } from '../../store/authStore'
import { clsx } from 'clsx'

const NAV = [
  { path: '/',          label: 'Home',      icon: Brain },
  { path: '/resume',    label: 'Resume',    icon: FileText },
  { path: '/interview', label: 'Interview', icon: Mic },
  { path: '/dashboard', label: 'Dashboard', icon: BarChart3 },
]

export default function Navbar() {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [open, setOpen] = useState(false)

  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <header className="sticky top-0 z-50 border-b" style={{ background: 'rgba(15,15,26,0.85)', backdropFilter: 'blur(20px)', borderColor: 'rgba(255,255,255,0.06)' }}>
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2.5 font-bold text-xl text-white no-underline">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
            <Brain size={18} className="text-white" />
          </div>
          <span>IntelliHire <span className="text-indigo-400">Pro</span></span>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-1">
          {NAV.map(({ path, label, icon: Icon }) => (
            <Link
              key={path}
              to={path}
              className={clsx(
                'flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium no-underline transition-all',
                pathname === path
                  ? 'bg-indigo-600/20 text-indigo-300'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              )}
            >
              <Icon size={15} />
              {label}
            </Link>
          ))}
        </nav>

        {/* Auth */}
        <div className="hidden md:flex items-center gap-3">
          {user ? (
            <>
              <span className="text-sm text-slate-400">
                Hi, <span className="text-white font-medium">{user.name.split(' ')[0]}</span>
              </span>
              <button onClick={handleLogout} className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-all cursor-pointer border-0 bg-transparent">
                <LogOut size={15} /> Logout
              </button>
            </>
          ) : (
            <Link to="/login" className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold no-underline transition-all">
              <LogIn size={15} /> Sign In
            </Link>
          )}
        </div>

        {/* Mobile toggle */}
        <button className="md:hidden p-2 text-slate-400 hover:text-white cursor-pointer border-0 bg-transparent" onClick={() => setOpen(!open)}>
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="md:hidden border-t px-4 py-3 space-y-1" style={{ background: 'rgba(15,15,26,0.98)', borderColor: 'rgba(255,255,255,0.06)' }}>
          {NAV.map(({ path, label, icon: Icon }) => (
            <Link key={path} to={path} onClick={() => setOpen(false)}
              className={clsx(
                'flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium no-underline transition-all',
                pathname === path ? 'bg-indigo-600/20 text-indigo-300' : 'text-slate-400 hover:text-white'
              )}>
              <Icon size={16} />{label}
            </Link>
          ))}
          <div className="pt-2 border-t" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
            {user ? (
              <button onClick={() => { handleLogout(); setOpen(false) }} className="w-full text-left flex items-center gap-2 px-3 py-2.5 text-sm text-red-400 cursor-pointer border-0 bg-transparent">
                <LogOut size={16} /> Logout
              </button>
            ) : (
              <Link to="/login" onClick={() => setOpen(false)} className="flex items-center gap-2 px-3 py-2.5 text-sm text-indigo-400 no-underline">
                <LogIn size={16} /> Sign In
              </Link>
            )}
          </div>
        </div>
      )}
    </header>
  )
}
