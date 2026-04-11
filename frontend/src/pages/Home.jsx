import { Link } from 'react-router-dom'
import { Brain, FileSearch, MessageSquare, BarChart3, ArrowRight, CheckCircle, Zap, Shield, Star } from 'lucide-react'
import { Button, Card } from '../components/ui'

const FEATURES = [
  {
    icon: FileSearch, title: 'AI Resume Analyzer',
    desc: 'Extract skills, experience, education, and get a comprehensive score. Powered by GPT-4.',
    color: 'from-indigo-500 to-violet-600', path: '/resume',
  },
  {
    icon: MessageSquare, title: 'Smart Question Generator',
    desc: 'Auto-generate tailored technical and behavioral questions based on the candidate\'s profile.',
    color: 'from-violet-500 to-pink-600', path: '/interview',
  },
  {
    icon: BarChart3, title: 'Intelligent Evaluation',
    desc: 'AI scores candidate answers with detailed feedback, strengths, and areas for improvement.',
    color: 'from-cyan-500 to-blue-600', path: '/interview',
  },
]

const STATS = [
  { value: '95%', label: 'Analysis Accuracy' },
  { value: '<3s', label: 'Response Time' },
  { value: '50+', label: 'Question Categories' },
  { value: '10x', label: 'Faster Screening' },
]

const WHY = [
  'GPT-4 powered deep analysis',
  'PDF & DOCX resume support',
  'Job description matching',
  'Fit score & gap analysis',
  'Behavioral + technical questions',
  'Answer scoring with feedback',
]

export default function Home() {
  return (
    <div className="flex-1">
      {/* Hero */}
      <section className="relative overflow-hidden py-24 px-4">
        <div className="absolute inset-0 pointer-events-none" style={{
          background: 'radial-gradient(ellipse 80% 60% at 50% -20%, rgba(99,102,241,0.3) 0%, transparent 70%)',
        }} />
        <div className="max-w-4xl mx-auto text-center relative">
          <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/20 rounded-full px-4 py-1.5 mb-6">
            <Zap size={14} className="text-indigo-400" />
            <span className="text-sm text-indigo-300 font-medium">AI-Powered Hiring Intelligence</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold text-white leading-tight mb-6">
            Hire Smarter with <br />
            <span style={{ background: 'linear-gradient(135deg,#6366f1,#8b5cf6,#06b6d4)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              AI at the Helm
            </span>
          </h1>
          <p className="text-xl text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed">
            Analyze resumes, generate interview questions, and evaluate candidates — all powered by GPT-4.
            Cut your screening time by 10x.
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <Link to="/resume">
              <Button size="lg" className="text-base">
                Analyze a Resume <ArrowRight size={18} />
              </Button>
            </Link>
            <Link to="/interview">
              <Button size="lg" variant="secondary" className="text-base">
                Start Interview Practice
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12 px-4 border-y" style={{ borderColor: 'rgba(255,255,255,0.06)', background: 'rgba(255,255,255,0.02)' }}>
        <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
          {STATS.map(({ value, label }) => (
            <div key={label} className="text-center">
              <p className="text-4xl font-extrabold text-transparent bg-clip-text" style={{ backgroundImage: 'linear-gradient(135deg,#6366f1,#8b5cf6)' }}>{value}</p>
              <p className="text-slate-400 text-sm mt-1">{label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-white mb-3">Everything You Need to Hire Better</h2>
            <p className="text-slate-400 max-w-xl mx-auto">Three powerful AI modules working together to transform your hiring workflow.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {FEATURES.map(({ icon: Icon, title, desc, color, path }) => (
              <Card key={title} hover className="group">
                <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${color} flex items-center justify-center mb-5`}>
                  <Icon size={22} className="text-white" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed mb-5">{desc}</p>
                <Link to={path} className="inline-flex items-center gap-1.5 text-sm text-indigo-400 hover:text-indigo-300 no-underline font-medium transition-colors group-hover:gap-2.5">
                  Try it now <ArrowRight size={14} />
                </Link>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Why */}
      <section className="py-20 px-4" style={{ background: 'rgba(255,255,255,0.02)' }}>
        <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-12 items-center">
          <div>
            <div className="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-3 py-1 mb-4">
              <Shield size={13} className="text-emerald-400" />
              <span className="text-xs text-emerald-300 font-medium">Production Ready</span>
            </div>
            <h2 className="text-3xl font-bold text-white mb-4">Why IntelliHire Pro?</h2>
            <p className="text-slate-400 mb-8 leading-relaxed">
              Built for modern teams that value speed and accuracy. Our AI analyses resumes in seconds and generates interview questions that actually reveal candidate depth.
            </p>
            <Link to="/resume">
              <Button>Get Started Free <ArrowRight size={16} /></Button>
            </Link>
          </div>
          <div className="grid grid-cols-1 gap-3">
            {WHY.map((item) => (
              <div key={item} className="flex items-center gap-3 p-4 rounded-xl" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)' }}>
                <CheckCircle size={18} className="text-emerald-400 flex-shrink-0" />
                <span className="text-sm text-slate-300">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <div className="max-w-2xl mx-auto text-center">
          <Star size={32} className="text-indigo-400 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-white mb-4">Ready to Transform Your Hiring?</h2>
          <p className="text-slate-400 mb-8">Upload your first resume and see AI-powered insights in under 10 seconds.</p>
          <Link to="/resume">
            <Button size="lg">Upload Resume Now <ArrowRight size={18} /></Button>
          </Link>
        </div>
      </section>
    </div>
  )
}
