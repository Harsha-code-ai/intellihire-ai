import { useState, useRef } from 'react'
import { Upload, FileText, Briefcase, CheckCircle, XCircle, ArrowRight, RefreshCw, Info } from 'lucide-react'
import toast from 'react-hot-toast'
import { resumeAPI } from '../services/api'
import {
  Button, Card, Badge, ProgressBar, ScoreRing, Input, Textarea, SectionHeader, Spinner
} from '../components/ui'

const DOMAIN_COLOR = {
  'AI/ML': 'purple', 'Web Development': 'blue', 'Data Science': 'cyan',
  'DevOps': 'green', 'Backend': 'blue', 'Frontend': 'cyan',
  'Full Stack': 'purple', 'Mobile Development': 'yellow',
  'Cybersecurity': 'red', 'Cloud': 'blue', 'General Software': 'default',
}

const DIFF_COLOR = { easy: 'green', medium: 'yellow', hard: 'red' }

export default function ResumePage() {
  const [file, setFile]             = useState(null)
  const [jobRole, setJobRole]       = useState('')
  const [jobDesc, setJobDesc]       = useState('')
  const [loading, setLoading]       = useState(false)
  const [result, setResult]         = useState(null)
  const [dragOver, setDragOver]     = useState(false)
  const fileRef = useRef()

  const handleFile = (f) => {
    if (!f) return
    const ok = f.name.match(/\.(pdf|docx|doc|txt)$/i)
    if (!ok) { toast.error('Please upload a PDF, DOCX, or TXT file'); return }
    if (f.size > 5 * 1024 * 1024) { toast.error('File must be under 5 MB'); return }
    setFile(f)
    setResult(null)
  }

  const onDrop = (e) => {
    e.preventDefault(); setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }

  const analyze = async () => {
    if (!file) { toast.error('Please upload a resume first'); return }
    setLoading(true)
    try {
      const { data } = await resumeAPI.upload(file, jobRole || null, jobDesc || null)
      setResult(data)
      toast.success('Resume analyzed successfully!')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const reset = () => { setFile(null); setResult(null); setJobRole(''); setJobDesc('') }

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <SectionHeader icon={FileText} title="AI Resume Analyzer" subtitle="Upload a resume and get deep AI-powered insights in seconds." />

      {!result ? (
        <div className="grid md:grid-cols-2 gap-6">
          {/* Upload Zone */}
          <Card>
            <h2 className="text-base font-semibold text-white mb-4">1. Upload Resume</h2>
            <div
              onClick={() => fileRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
              onDragLeave={() => setDragOver(false)}
              onDrop={onDrop}
              className="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all"
              style={{ borderColor: dragOver ? '#6366f1' : 'rgba(255,255,255,0.12)', background: dragOver ? 'rgba(99,102,241,0.08)' : 'rgba(255,255,255,0.02)' }}
            >
              <input ref={fileRef} type="file" accept=".pdf,.docx,.doc,.txt" className="hidden" onChange={(e) => handleFile(e.target.files[0])} />
              <Upload size={36} className="mx-auto text-slate-500 mb-3" />
              {file ? (
                <>
                  <p className="text-white font-medium">{file.name}</p>
                  <p className="text-slate-500 text-xs mt-1">{(file.size / 1024).toFixed(1)} KB</p>
                </>
              ) : (
                <>
                  <p className="text-slate-300 font-medium">Drop your resume here</p>
                  <p className="text-slate-500 text-sm mt-1">PDF, DOCX, or TXT — max 5 MB</p>
                </>
              )}
            </div>
          </Card>

          {/* Job Match */}
          <Card>
            <h2 className="text-base font-semibold text-white mb-4">2. Job Match <span className="text-slate-500 font-normal text-xs">(optional)</span></h2>
            <div className="space-y-4">
              <Input label="Job Role" placeholder="e.g. Senior Frontend Developer" value={jobRole} onChange={(e) => setJobRole(e.target.value)} />
              <Textarea label="Job Description" placeholder="Paste the job description here for a detailed fit analysis..." rows={6} value={jobDesc} onChange={(e) => setJobDesc(e.target.value)} />
            </div>
          </Card>

          <div className="md:col-span-2 flex gap-3">
            <Button onClick={analyze} loading={loading} size="lg" className="flex-1">
              {loading ? 'Analyzing...' : 'Analyze Resume'} {!loading && <ArrowRight size={18} />}
            </Button>
          </div>
        </div>
      ) : (
        <ResultView result={result} onReset={reset} />
      )}
    </div>
  )
}

function ResultView({ result, onReset }) {
  const scoreBreakdown = result.score_breakdown || {}
  const skills = result.skills || []
  const education = result.education || []
  const improvements = result.improvements || []
  const fitBreakdown = result.fit_breakdown || {}
  const strengths = result.strengths || []
  const gaps = result.gaps || []

  return (
    <div className="space-y-6">
      {/* Top row */}
      <div className="grid md:grid-cols-3 gap-6">
        {/* Identity */}
        <Card className="md:col-span-2">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-1">
                <h2 className="text-xl font-bold text-white">{result.candidate_name || 'Candidate'}</h2>
                {result.domain && <Badge color={DOMAIN_COLOR[result.domain] || 'default'}>{result.domain}</Badge>}
              </div>
              {result.candidate_email && <p className="text-slate-400 text-sm mb-3">{result.candidate_email}</p>}
              <p className="text-slate-300 text-sm leading-relaxed">{result.summary || 'No summary available.'}</p>
              {result.experience_years > 0 && (
                <p className="text-slate-400 text-sm mt-3">
                  <span className="text-white font-medium">{result.experience_years} years</span> of experience
                </p>
              )}
            </div>
            <div className="flex gap-4 flex-shrink-0">
              <ScoreRing score={result.resume_score} label="Resume" />
              {result.fit_score > 0 && <ScoreRing score={result.fit_score} label="Fit" />}
            </div>
          </div>
        </Card>

        {/* Quick Stats */}
        <Card>
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Score Breakdown</h3>
          <div className="space-y-3">
            {Object.entries(scoreBreakdown).map(([key, val]) => (
              <ProgressBar
                key={key}
                value={val}
                max={key === 'skills_relevance' || key === 'experience_depth' ? 25 : key === 'education_quality' ? 20 : 15}
                label={key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
              />
            ))}
          </div>
        </Card>
      </div>

      {/* Skills */}
      <Card>
        <h3 className="text-base font-semibold text-white mb-4">Skills Detected ({skills.length})</h3>
        <div className="flex flex-wrap gap-2">
          {skills.length > 0
            ? skills.map((s) => <Badge key={s} color="blue">{s}</Badge>)
            : <p className="text-slate-500 text-sm">No skills extracted.</p>
          }
        </div>
      </Card>

      {/* Education */}
      {education.length > 0 && (
        <Card>
          <h3 className="text-base font-semibold text-white mb-4">Education</h3>
          <div className="space-y-2">
            {education.map((e, i) => (
              <div key={i} className="flex items-center gap-2.5">
                <CheckCircle size={15} className="text-emerald-400 flex-shrink-0" />
                <span className="text-slate-300 text-sm">{e}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Job Fit */}
      {result.job_role && (
        <Card>
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="text-base font-semibold text-white">Job Fit — {result.job_role}</h3>
              <p className="text-slate-400 text-xs mt-0.5">How well the candidate matches this role</p>
            </div>
            <Badge color={result.fit_score >= 70 ? 'green' : result.fit_score >= 40 ? 'yellow' : 'red'}>
              {result.fit_score}% match
            </Badge>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <div>
              <p className="text-sm font-medium text-slate-400 mb-3">Score Breakdown</p>
              <div className="space-y-3">
                {Object.entries(fitBreakdown).map(([k, v]) => (
                  <ProgressBar key={k} value={v} max={k === 'skills_match' ? 40 : k === 'experience_match' ? 30 : k === 'domain_alignment' ? 20 : 10} label={k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())} />
                ))}
              </div>
            </div>
            <div className="space-y-4">
              {strengths.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-emerald-400 mb-2">Strengths</p>
                  {strengths.map((s, i) => (
                    <div key={i} className="flex gap-2 items-start text-sm text-slate-300 mb-1.5">
                      <CheckCircle size={14} className="text-emerald-400 flex-shrink-0 mt-0.5" /> {s}
                    </div>
                  ))}
                </div>
              )}
              {gaps.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-red-400 mb-2">Gaps</p>
                  {gaps.map((g, i) => (
                    <div key={i} className="flex gap-2 items-start text-sm text-slate-300 mb-1.5">
                      <XCircle size={14} className="text-red-400 flex-shrink-0 mt-0.5" /> {g}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </Card>
      )}

      {/* Improvements */}
      {improvements.length > 0 && (
        <Card>
          <div className="flex items-center gap-2 mb-4">
            <Info size={16} className="text-amber-400" />
            <h3 className="text-base font-semibold text-white">Improvement Suggestions</h3>
          </div>
          <div className="space-y-2">
            {improvements.map((tip, i) => (
              <div key={i} className="flex gap-3 items-start p-3 rounded-xl" style={{ background: 'rgba(251,191,36,0.08)', border: '1px solid rgba(251,191,36,0.15)' }}>
                <span className="text-amber-400 font-bold text-sm flex-shrink-0">{i + 1}.</span>
                <p className="text-slate-300 text-sm">{tip}</p>
              </div>
            ))}
          </div>
        </Card>
      )}

      <div className="flex gap-3">
        <Button onClick={onReset} variant="secondary">
          <RefreshCw size={16} /> Analyze Another
        </Button>
        <Button onClick={() => window.location.href = '/interview'} variant="outline">
          Generate Interview Questions <ArrowRight size={16} />
        </Button>
      </div>
    </div>
  )
}
