import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Brain, Eye, EyeOff } from 'lucide-react'
import toast from 'react-hot-toast'
import { authAPI } from '../services/api'
import { useAuthStore } from '../store/authStore'
import { Button, Input, Card } from '../components/ui'

/* ─── Login ─────────────────────────────────────────────── */
export function LoginPage() {
  const [form,    setForm]    = useState({ email: '', password: '' })
  const [showPw,  setShowPw]  = useState(false)
  const [loading, setLoading] = useState(false)
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  const handle = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    if (!form.email || !form.password) { toast.error('Fill in all fields'); return }
    setLoading(true)
    try {
      const { data } = await authAPI.login(form)
      setAuth(data.user, data.access_token)
      toast.success(`Welcome back, ${data.user.name.split(' ')[0]}!`)
      navigate('/dashboard')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Login failed')
    } finally { setLoading(false) }
  }

  return <AuthLayout title="Welcome back" subtitle="Sign in to your IntelliHire account">
    <form onSubmit={submit} className="space-y-4">
      <Input label="Email" type="email" placeholder="you@example.com" value={form.email} onChange={handle('email')} autoComplete="email" />
      <div className="space-y-1.5">
        <label className="block text-sm font-medium text-slate-300">Password</label>
        <div className="relative">
          <input type={showPw ? 'text' : 'password'} placeholder="••••••••" value={form.password} onChange={handle('password')}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500/60 focus:ring-2 focus:ring-indigo-500/20 transition pr-10"
            autoComplete="current-password"
          />
          <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-3 text-slate-400 hover:text-white cursor-pointer border-0 bg-transparent">
            {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </div>
      </div>
      <Button type="submit" loading={loading} className="w-full" size="lg">Sign In</Button>
    </form>
    <p className="text-center text-sm text-slate-400 mt-6">
      Don't have an account?{' '}
      <Link to="/register" className="text-indigo-400 hover:text-indigo-300 no-underline font-medium">Create one</Link>
    </p>
    <DemoHint />
  </AuthLayout>
}

/* ─── Register ───────────────────────────────────────────── */
export function RegisterPage() {
  const [form,    setForm]    = useState({ name: '', email: '', password: '', confirm: '' })
  const [showPw,  setShowPw]  = useState(false)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handle = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    if (!form.name || !form.email || !form.password) { toast.error('Fill in all fields'); return }
    if (form.password.length < 6) { toast.error('Password must be at least 6 characters'); return }
    if (form.password !== form.confirm) { toast.error('Passwords do not match'); return }
    setLoading(true)
    try {
      await authAPI.register({ name: form.name, email: form.email, password: form.password })
      toast.success('Account created! Please sign in.')
      navigate('/login')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Registration failed')
    } finally { setLoading(false) }
  }

  return <AuthLayout title="Create account" subtitle="Join IntelliHire Pro today — it's free">
    <form onSubmit={submit} className="space-y-4">
      <Input label="Full Name" placeholder="Jane Smith" value={form.name} onChange={handle('name')} autoComplete="name" />
      <Input label="Email" type="email" placeholder="you@example.com" value={form.email} onChange={handle('email')} autoComplete="email" />
      <div className="space-y-1.5">
        <label className="block text-sm font-medium text-slate-300">Password</label>
        <div className="relative">
          <input type={showPw ? 'text' : 'password'} placeholder="At least 6 characters" value={form.password} onChange={handle('password')}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500/60 transition pr-10"
          />
          <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-3 text-slate-400 hover:text-white cursor-pointer border-0 bg-transparent">
            {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </div>
      </div>
      <Input label="Confirm Password" type={showPw ? 'text' : 'password'} placeholder="Repeat password" value={form.confirm} onChange={handle('confirm')} />
      <Button type="submit" loading={loading} className="w-full" size="lg">Create Account</Button>
    </form>
    <p className="text-center text-sm text-slate-400 mt-6">
      Already have an account?{' '}
      <Link to="/login" className="text-indigo-400 hover:text-indigo-300 no-underline font-medium">Sign in</Link>
    </p>
  </AuthLayout>
}

/* ─── Shared layout ──────────────────────────────────────── */
function AuthLayout({ title, subtitle, children }) {
  return (
    <div className="flex-1 flex items-center justify-center px-4 py-16">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center mx-auto mb-4">
            <Brain size={26} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">{title}</h1>
          <p className="text-slate-400 text-sm mt-1">{subtitle}</p>
        </div>
        <Card>{children}</Card>
      </div>
    </div>
  )
}

function DemoHint() {
  return (
    <div className="mt-4 p-3 rounded-xl text-xs text-slate-400 text-center" style={{ background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.15)' }}>
      💡 You can use Resume Analyzer and Interview Practice without an account. Login is optional.
    </div>
  )
}
