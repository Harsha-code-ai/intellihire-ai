import { useEffect, useState } from 'react'
import { BarChart3, FileText, Mic, TrendingUp, Trash2, ExternalLink, Calendar } from 'lucide-react'
import { Link } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, RadarChart,
  PolarGrid, PolarAngleAxis, Radar
} from 'recharts'
import toast from 'react-hot-toast'
import { resumeAPI, interviewAPI } from '../services/api'
import { Card, Badge, Button, SectionHeader, EmptyState, Spinner, ProgressBar } from '../components/ui'

const DIFF_COLOR = { easy: 'green', medium: 'yellow', hard: 'red' }
const CAT_COLOR  = { technical: 'blue', behavioral: 'purple' }
const CORRECT_COLOR = { yes: 'green', partial: 'yellow', no: 'red' }

export default function Dashboard() {
  const [resumes,    setResumes]    = useState([])
  const [interviews, setInterviews] = useState([])
  const [loading,    setLoading]    = useState(true)
  const [tab,        setTab]        = useState('overview') // overview | resumes | interviews

  useEffect(() => {
    loadAll()
  }, [])

  const loadAll = async () => {
    setLoading(true)
    try {
      const [rRes, iRes] = await Promise.allSettled([
        resumeAPI.history(),
        interviewAPI.history(),
      ])
      if (rRes.status === 'fulfilled') setResumes(rRes.value.data || [])
      if (iRes.status === 'fulfilled') setInterviews(iRes.value.data || [])
    } catch (_) {}
    finally { setLoading(false) }
  }

  const deleteInterview = async (id) => {
    try {
      await interviewAPI.delete(id)
      setInterviews(prev => prev.filter(i => i.id !== id))
      toast.success('Deleted')
    } catch {
      toast.error('Delete failed')
    }
  }

  /* ── Computed stats ── */
  const avgInterviewScore = interviews.length
    ? (interviews.filter(i => i.score != null).reduce((s, i) => s + i.score, 0) / interviews.filter(i => i.score != null).length).toFixed(1)
    : 0

  const avgResumeScore = resumes.length
    ? (resumes.filter(r => r.resume_score).reduce((s, r) => s + r.resume_score, 0) / resumes.filter(r => r.resume_score).length).toFixed(1)
    : 0

  // Score distribution for bar chart
  const scoreBuckets = [
    { name: '0-2', count: 0 }, { name: '3-4', count: 0 }, { name: '5-6', count: 0 },
    { name: '7-8', count: 0 }, { name: '9-10', count: 0 },
  ]
  interviews.forEach(i => {
    const s = i.score || 0
    if (s <= 2) scoreBuckets[0].count++
    else if (s <= 4) scoreBuckets[1].count++
    else if (s <= 6) scoreBuckets[2].count++
    else if (s <= 8) scoreBuckets[3].count++
    else scoreBuckets[4].count++
  })

  // Difficulty breakdown
  const diffMap = { easy: 0, medium: 0, hard: 0 }
  interviews.forEach(i => { if (diffMap[i.difficulty] !== undefined) diffMap[i.difficulty]++ })
  const radarData = [
    { subject: 'Easy',   score: diffMap.easy },
    { subject: 'Medium', score: diffMap.medium },
    { subject: 'Hard',   score: diffMap.hard },
  ]

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Spinner size="lg" />
    </div>
  )

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <SectionHeader icon={BarChart3} title="Dashboard" subtitle="Your hiring activity at a glance." />

      {/* Tab Bar */}
      <div className="flex gap-1 mb-8 p-1 rounded-xl w-fit" style={{ background: 'rgba(255,255,255,0.05)' }}>
        {['overview', 'resumes', 'interviews'].map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-sm font-medium capitalize cursor-pointer border-0 transition-all ${
              tab === t ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white bg-transparent'
            }`}>
            {t}
          </button>
        ))}
      </div>

      {tab === 'overview' && <OverviewTab resumes={resumes} interviews={interviews} avgInterviewScore={avgInterviewScore} avgResumeScore={avgResumeScore} scoreBuckets={scoreBuckets} radarData={radarData} />}
      {tab === 'resumes'    && <ResumesTab resumes={resumes} />}
      {tab === 'interviews' && <InterviewsTab interviews={interviews} onDelete={deleteInterview} />}
    </div>
  )
}

/* ── Overview ────────────────────────────────────────────── */
function OverviewTab({ resumes, interviews, avgInterviewScore, avgResumeScore, scoreBuckets, radarData }) {
  const stats = [
    { icon: FileText, label: 'Resumes Analyzed',    value: resumes.length,    color: '#6366f1' },
    { icon: Mic,      label: 'Questions Practiced',  value: interviews.length, color: '#8b5cf6' },
    { icon: TrendingUp, label: 'Avg Interview Score', value: `${avgInterviewScore}/10`, color: '#10b981' },
    { icon: TrendingUp, label: 'Avg Resume Score',    value: `${avgResumeScore}%`,      color: '#06b6d4' },
  ]

  return (
    <div className="space-y-6">
      {/* Stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map(({ icon: Icon, label, value, color }) => (
          <Card key={label}>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: color + '22' }}>
                <Icon size={16} style={{ color }} />
              </div>
            </div>
            <p className="text-2xl font-extrabold text-white">{value}</p>
            <p className="text-xs text-slate-400 mt-0.5">{label}</p>
          </Card>
        ))}
      </div>

      {interviews.length > 0 && (
        <div className="grid md:grid-cols-2 gap-6">
          {/* Score distribution */}
          <Card>
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Score Distribution</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={scoreBuckets} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} allowDecimals={false} />
                <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#fff' }} />
                <Bar dataKey="count" fill="#6366f1" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Difficulty radar */}
          <Card>
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Questions by Difficulty</h3>
            <ResponsiveContainer width="100%" height={200}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <Radar dataKey="score" stroke="#6366f1" fill="#6366f1" fillOpacity={0.3} />
              </RadarChart>
            </ResponsiveContainer>
          </Card>
        </div>
      )}

      {resumes.length === 0 && interviews.length === 0 && (
        <EmptyState icon={BarChart3}
          title="No activity yet"
          description="Analyze a resume or practice an interview to see your progress."
          action={
            <div className="flex gap-3">
              <Link to="/resume"><Button size="sm"><FileText size={14} /> Analyze Resume</Button></Link>
              <Link to="/interview"><Button size="sm" variant="secondary"><Mic size={14} /> Practice Interview</Button></Link>
            </div>
          }
        />
      )}
    </div>
  )
}

/* ── Resumes Tab ─────────────────────────────────────────── */
function ResumesTab({ resumes }) {
  if (!resumes.length) return (
    <EmptyState icon={FileText} title="No resumes analyzed yet"
      description="Upload your first resume to see results here."
      action={<Link to="/resume"><Button size="sm"><FileText size={14} /> Upload Resume</Button></Link>}
    />
  )
  return (
    <div className="space-y-3">
      {resumes.map(r => (
        <Card key={r.id} className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center flex-shrink-0">
            <FileText size={18} className="text-indigo-400" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white font-medium truncate">{r.filename}</p>
            <div className="flex items-center gap-2 mt-1 flex-wrap">
              {r.domain && <Badge color="blue">{r.domain}</Badge>}
              {r.job_role && <Badge color="purple">{r.job_role}</Badge>}
              <span className="text-xs text-slate-500 flex items-center gap-1">
                <Calendar size={10} /> {r.created_at ? new Date(r.created_at).toLocaleDateString() : ''}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-4 flex-shrink-0">
            {r.resume_score != null && (
              <div className="text-center">
                <p className="text-lg font-bold text-indigo-300">{Math.round(r.resume_score)}</p>
                <p className="text-xs text-slate-500">Score</p>
              </div>
            )}
            {r.fit_score > 0 && (
              <div className="text-center">
                <p className="text-lg font-bold text-emerald-300">{Math.round(r.fit_score)}%</p>
                <p className="text-xs text-slate-500">Fit</p>
              </div>
            )}
            <Link to={`/resume`}>
              <Button variant="ghost" size="sm"><ExternalLink size={14} /></Button>
            </Link>
          </div>
        </Card>
      ))}
    </div>
  )
}

/* ── Interviews Tab ──────────────────────────────────────── */
function InterviewsTab({ interviews, onDelete }) {
  if (!interviews.length) return (
    <EmptyState icon={Mic} title="No interview sessions saved"
      description="Complete and save an interview session to see it here."
      action={<Link to="/interview"><Button size="sm"><Mic size={14} /> Start Interview</Button></Link>}
    />
  )
  return (
    <div className="space-y-3">
      {interviews.map(i => (
        <Card key={i.id}>
          <div className="flex items-start gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                <span className="text-white font-medium text-sm">{i.role}</span>
                <Badge color={DIFF_COLOR[i.difficulty]}>{i.difficulty}</Badge>
                <Badge color={CAT_COLOR[i.category]}>{i.category}</Badge>
                {i.is_correct && <Badge color={CORRECT_COLOR[i.is_correct]}>{i.is_correct}</Badge>}
              </div>
              <p className="text-slate-400 text-sm mb-2 leading-relaxed">{i.question}</p>
              {i.answer && <p className="text-slate-500 text-xs truncate">{i.answer}</p>}
              {i.feedback && <p className="text-slate-400 text-xs mt-2 italic">"{i.feedback}"</p>}
              <p className="text-slate-600 text-xs mt-2 flex items-center gap-1">
                <Calendar size={10} /> {i.created_at ? new Date(i.created_at).toLocaleString() : ''}
              </p>
            </div>
            <div className="flex items-center gap-3 flex-shrink-0">
              {i.score != null && (
                <div className="text-center">
                  <p className="text-xl font-bold text-indigo-300">{i.score}</p>
                  <p className="text-xs text-slate-500">/10</p>
                </div>
              )}
              <Button variant="ghost" size="sm" onClick={() => onDelete(i.id)} className="text-red-400 hover:text-red-300">
                <Trash2 size={14} />
              </Button>
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}
