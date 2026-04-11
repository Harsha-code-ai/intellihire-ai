import { clsx } from 'clsx'

/* ─── Button ───────────────────────────────────────────────────────────── */
export function Button({ children, variant = 'primary', size = 'md', loading, disabled, className, ...props }) {
  const base = 'inline-flex items-center justify-center gap-2 font-semibold rounded-xl transition-all duration-200 cursor-pointer border-0 outline-none'
  const variants = {
    primary:  'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-900/40',
    secondary:'bg-white/10 hover:bg-white/20 text-white border border-white/10',
    success:  'bg-emerald-600 hover:bg-emerald-500 text-white',
    danger:   'bg-red-600 hover:bg-red-500 text-white',
    ghost:    'bg-transparent hover:bg-white/10 text-slate-300',
    outline:  'bg-transparent border border-indigo-500 text-indigo-400 hover:bg-indigo-500/10',
  }
  const sizes = { sm: 'px-3 py-1.5 text-sm', md: 'px-5 py-2.5 text-sm', lg: 'px-7 py-3 text-base' }
  return (
    <button
      className={clsx(base, variants[variant], sizes[size], (disabled || loading) && 'opacity-50 cursor-not-allowed', className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Spinner size="sm" />}
      {children}
    </button>
  )
}

/* ─── Card ─────────────────────────────────────────────────────────────── */
export function Card({ children, className, hover, ...props }) {
  return (
    <div
      className={clsx(
        'rounded-2xl border border-white/8 p-6',
        'bg-gradient-to-br from-slate-900/80 to-slate-800/40 backdrop-blur-sm',
        hover && 'transition-transform duration-300 hover:-translate-y-1 hover:border-indigo-500/30',
        className
      )}
      style={{ borderColor: 'rgba(255,255,255,0.08)' }}
      {...props}
    >
      {children}
    </div>
  )
}

/* ─── Badge ────────────────────────────────────────────────────────────── */
export function Badge({ children, color = 'default', className }) {
  const colors = {
    default:  'bg-white/10 text-slate-300',
    blue:     'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30',
    green:    'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30',
    yellow:   'bg-amber-500/20 text-amber-300 border border-amber-500/30',
    red:      'bg-red-500/20 text-red-300 border border-red-500/30',
    purple:   'bg-violet-500/20 text-violet-300 border border-violet-500/30',
    cyan:     'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30',
  }
  return (
    <span className={clsx('inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium', colors[color], className)}>
      {children}
    </span>
  )
}

/* ─── Spinner ──────────────────────────────────────────────────────────── */
export function Spinner({ size = 'md', color = 'white' }) {
  const sizes = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-10 h-10' }
  return (
    <div
      className={clsx('border-2 border-white/20 rounded-full animate-spin', sizes[size])}
      style={{ borderTopColor: color === 'white' ? '#fff' : '#6366f1' }}
    />
  )
}

/* ─── ProgressBar ──────────────────────────────────────────────────────── */
export function ProgressBar({ value = 0, max = 100, color, label, showValue = true }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100))
  const auto = pct >= 70 ? '#10b981' : pct >= 40 ? '#f59e0b' : '#ef4444'
  const barColor = color || auto
  return (
    <div className="space-y-1">
      {(label || showValue) && (
        <div className="flex justify-between text-xs text-slate-400">
          {label && <span>{label}</span>}
          {showValue && <span className="font-semibold" style={{ color: barColor }}>{Math.round(pct)}%</span>}
        </div>
      )}
      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700 ease-out"
          style={{ width: `${pct}%`, backgroundColor: barColor }}
        />
      </div>
    </div>
  )
}

/* ─── Input ────────────────────────────────────────────────────────────── */
export function Input({ label, error, className, ...props }) {
  return (
    <div className="space-y-1.5">
      {label && <label className="block text-sm font-medium text-slate-300">{label}</label>}
      <input
        className={clsx(
          'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white placeholder-slate-500',
          'focus:outline-none focus:border-indigo-500/60 focus:ring-2 focus:ring-indigo-500/20 transition',
          error && 'border-red-500/60',
          className
        )}
        {...props}
      />
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  )
}

/* ─── Textarea ─────────────────────────────────────────────────────────── */
export function Textarea({ label, error, className, ...props }) {
  return (
    <div className="space-y-1.5">
      {label && <label className="block text-sm font-medium text-slate-300">{label}</label>}
      <textarea
        className={clsx(
          'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 resize-none',
          'focus:outline-none focus:border-indigo-500/60 focus:ring-2 focus:ring-indigo-500/20 transition',
          error && 'border-red-500/60',
          className
        )}
        {...props}
      />
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  )
}

/* ─── ScoreRing ────────────────────────────────────────────────────────── */
export function ScoreRing({ score = 0, max = 100, size = 120, label = 'Score' }) {
  const pct = Math.min(100, Math.max(0, (score / max) * 100))
  const r = 45
  const circ = 2 * Math.PI * r
  const offset = circ - (pct / 100) * circ
  const color = pct >= 70 ? '#10b981' : pct >= 40 ? '#f59e0b' : '#ef4444'
  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={r} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="8" />
        <circle
          cx="50" cy="50" r={r} fill="none"
          stroke={color} strokeWidth="8"
          strokeDasharray={circ} strokeDashoffset={offset}
          strokeLinecap="round" transform="rotate(-90 50 50)"
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
        <text x="50" y="50" textAnchor="middle" dominantBaseline="central" fill="white" fontSize="18" fontWeight="700">
          {Math.round(score)}
        </text>
      </svg>
      <span className="text-xs text-slate-400 font-medium">{label}</span>
    </div>
  )
}

/* ─── SectionHeader ────────────────────────────────────────────────────── */
export function SectionHeader({ icon: Icon, title, subtitle }) {
  return (
    <div className="flex items-start gap-4 mb-8">
      {Icon && (
        <div className="w-12 h-12 rounded-2xl bg-indigo-500/20 flex items-center justify-center flex-shrink-0">
          <Icon size={22} className="text-indigo-400" />
        </div>
      )}
      <div>
        <h1 className="text-2xl font-bold text-white">{title}</h1>
        {subtitle && <p className="text-slate-400 text-sm mt-0.5">{subtitle}</p>}
      </div>
    </div>
  )
}

/* ─── EmptyState ───────────────────────────────────────────────────────── */
export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center gap-4">
      {Icon && (
        <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center">
          <Icon size={28} className="text-slate-500" />
        </div>
      )}
      <div>
        <p className="text-slate-300 font-medium">{title}</p>
        {description && <p className="text-slate-500 text-sm mt-1">{description}</p>}
      </div>
      {action}
    </div>
  )
}
