import { useState } from 'react'
import {
  Mic, ChevronRight, RotateCcw, Save,
  CheckCircle, XCircle, Minus, Brain, Settings
} from 'lucide-react'
import toast from 'react-hot-toast'
import { interviewAPI } from '../services/api'
import { Button, Card, Badge, ScoreRing, Input, Textarea, SectionHeader } from '../components/ui'

const DIFFICULTIES = ['easy', 'medium', 'hard', 'mixed']
const COUNTS       = [3, 5, 8, 10]
const DIFF_COLOR   = { easy: 'green', medium: 'yellow', hard: 'red', mixed: 'blue' }
const CAT_COLOR    = { technical: 'blue', behavioral: 'purple' }

function correctIcon(v) {
  if (v === 'yes')     return <CheckCircle size={15} style={{ color: '#10b981' }} />
  if (v === 'partial') return <Minus       size={15} style={{ color: '#f59e0b' }} />
  return                      <XCircle     size={15} style={{ color: '#ef4444' }} />
}

export default function InterviewPage() {
  const [role,         setRole]         = useState('')
  const [skills,       setSkills]       = useState('')
  const [difficulty,   setDifficulty]   = useState('mixed')
  const [numQ,         setNumQ]         = useState(5)
  const [behavioral,   setBehavioral]   = useState(true)
  const [questions,    setQuestions]    = useState([])
  const [activeIdx,    setActiveIdx]    = useState(0)
  const [answers,      setAnswers]      = useState({})
  const [evaluations,  setEvaluations]  = useState({})
  const [loadingGen,   setLoadingGen]   = useState(false)
  const [loadingEval,  setLoadingEval]  = useState({})
  const [loadingSave,  setLoadingSave]  = useState({})
  const [showAdv,      setShowAdv]      = useState(false)
  const [phase,        setPhase]        = useState('setup')

  const generateQuestions = async () => {
    if (!role.trim()) { toast.error('Enter a job role'); return }
    setLoadingGen(true)
    try {
      const skillList = skills.split(',').map(s => s.trim()).filter(Boolean)
      const { data } = await interviewAPI.generateQuestions({
        role, skills: skillList, difficulty,
        num_questions: numQ, include_behavioral: behavioral,
      })
      setQuestions(data); setAnswers({}); setEvaluations({})
      setActiveIdx(0); setPhase('interview')
      toast.success(`${data.length} questions generated!`)
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Generation failed')
    } finally { setLoadingGen(false) }
  }

  const evaluate = async (idx) => {
    const q = questions[idx]; const a = answers[idx]
    if (!a?.trim()) { toast.error('Write your answer first'); return }
    setLoadingEval(p => ({ ...p, [idx]: true }))
    try {
      const { data } = await interviewAPI.evaluateAnswer({ question: q.question, answer: a, role })
      setEvaluations(p => ({ ...p, [idx]: data }))
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Evaluation failed')
    } finally { setLoadingEval(p => ({ ...p, [idx]: false })) }
  }

  const saveRecord = async (idx) => {
    const q = questions[idx]; const ev = evaluations[idx]
    if (!ev) { toast.error('Evaluate before saving'); return }
    setLoadingSave(p => ({ ...p, [idx]: true }))
    try {
      await interviewAPI.save({
        role, question: q.question, difficulty: q.difficulty,
        category: q.category, answer: answers[idx],
        score: ev.score, feedback: ev.feedback, is_correct: ev.is_correct,
      })
      toast.success('Saved!')
    } catch { toast.error('Save failed') }
    finally { setLoadingSave(p => ({ ...p, [idx]: false })) }
  }

  const reset = () => {
    setPhase('setup'); setQuestions([])
    setAnswers({}); setEvaluations({})
  }

  const allEvaled = questions.length > 0 && questions.every((_, i) => evaluations[i])
  const avgScore  = allEvaled
    ? (Object.values(evaluations).reduce((s, e) => s + (e.score || 0), 0) / questions.length).toFixed(1)
    : null

  /* ── SETUP ───────────────────────────────── */
  if (phase === 'setup') {
    return (
      <div style={{ maxWidth: 560, margin: '0 auto', padding: '40px 16px' }}>
        <SectionHeader icon={Mic} title="Interview Practice"
          subtitle="Generate AI-powered questions tailored to any role." />
        <Card className="space-y-5">
          <Input label="Job Role *" placeholder="e.g. Senior React Developer, Data Scientist"
            value={role} onChange={e => setRole(e.target.value)} />
          <Input label="Key Skills (comma-separated, optional)"
            placeholder="e.g. React, TypeScript, Node.js"
            value={skills} onChange={e => setSkills(e.target.value)} />

          <button onClick={() => setShowAdv(!showAdv)} style={{
            background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer',
            display: 'flex', alignItems: 'center', gap: 6, fontSize: 13,
          }}>
            <Settings size={13} /> Advanced {showAdv ? '▲' : '▼'}
          </button>

          {showAdv && (
            <div style={{ paddingLeft: 14, borderLeft: '2px solid rgba(99,102,241,0.3)' }}>
              <p style={{ color: '#cbd5e1', fontSize: 13, marginBottom: 8 }}>Difficulty</p>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 16 }}>
                {DIFFICULTIES.map(d => (
                  <button key={d} onClick={() => setDifficulty(d)} style={{
                    padding: '5px 12px', borderRadius: 8, fontSize: 12, fontWeight: 600,
                    textTransform: 'capitalize', cursor: 'pointer',
                    background: difficulty === d ? '#4f46e5' : 'rgba(255,255,255,0.05)',
                    border: difficulty === d ? '1px solid #6366f1' : '1px solid rgba(255,255,255,0.1)',
                    color: difficulty === d ? 'white' : '#94a3b8',
                  }}>{d}</button>
                ))}
              </div>
              <p style={{ color: '#cbd5e1', fontSize: 13, marginBottom: 8 }}>Count</p>
              <div style={{ display: 'flex', gap: 6, marginBottom: 16 }}>
                {COUNTS.map(n => (
                  <button key={n} onClick={() => setNumQ(n)} style={{
                    width: 40, padding: '5px 0', borderRadius: 8, fontSize: 14, fontWeight: 600,
                    cursor: 'pointer',
                    background: numQ === n ? '#4f46e5' : 'rgba(255,255,255,0.05)',
                    border: numQ === n ? '1px solid #6366f1' : '1px solid rgba(255,255,255,0.1)',
                    color: numQ === n ? 'white' : '#94a3b8',
                  }}>{n}</button>
                ))}
              </div>
              <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
                <div onClick={() => setBehavioral(!behavioral)} style={{
                  width: 38, height: 20, borderRadius: 10, cursor: 'pointer', position: 'relative',
                  background: behavioral ? '#4f46e5' : 'rgba(255,255,255,0.1)', transition: 'background 0.2s',
                }}>
                  <span style={{
                    position: 'absolute', top: 2, width: 16, height: 16, background: 'white',
                    borderRadius: '50%', transition: 'transform 0.2s',
                    transform: behavioral ? 'translateX(20px)' : 'translateX(2px)',
                  }} />
                </div>
                <span style={{ color: '#cbd5e1', fontSize: 13 }}>Include behavioral questions</span>
              </label>
            </div>
          )}

          <Button onClick={generateQuestions} loading={loadingGen} size="lg" className="w-full">
            {loadingGen ? 'Generating...' : `Generate ${numQ} Questions`}
            {!loadingGen && <ChevronRight size={17} />}
          </Button>
        </Card>
      </div>
    )
  }

  /* ── INTERVIEW ───────────────────────────── */
  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: '40px 16px' }}>
      <SectionHeader icon={Mic} title="Interview Session"
        subtitle={`${role} · ${questions.length} questions`} />

      <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr', gap: 24 }}>
        {/* Sidebar */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {questions.map((q, i) => {
            const ev = evaluations[i]
            return (
              <button key={i} onClick={() => setActiveIdx(i)} style={{
                textAlign: 'left', padding: 10, borderRadius: 10, cursor: 'pointer',
                background: i === activeIdx ? 'rgba(99,102,241,0.12)' : 'rgba(255,255,255,0.03)',
                border: i === activeIdx ? '1px solid rgba(99,102,241,0.4)' : '1px solid rgba(255,255,255,0.07)',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span style={{ fontSize: 10, color: '#64748b', fontWeight: 500 }}>Q{i + 1}</span>
                  <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
                    <Badge color={DIFF_COLOR[q.difficulty]}>{q.difficulty}</Badge>
                    {ev && correctIcon(ev.is_correct)}
                  </div>
                </div>
                <p style={{
                  fontSize: 11, color: '#cbd5e1', lineHeight: 1.4,
                  overflow: 'hidden', display: '-webkit-box',
                  WebkitLineClamp: 2, WebkitBoxOrient: 'vertical',
                }}>
                  {q.question}
                </p>
                {ev && (
                  <div style={{ marginTop: 5, display: 'flex', gap: 5, alignItems: 'center' }}>
                    <div style={{ flex: 1, height: 2, background: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
                      <div style={{ height: 2, background: '#6366f1', width: `${ev.score * 10}%`, borderRadius: 1 }} />
                    </div>
                    <span style={{ fontSize: 10, color: '#818cf8' }}>{ev.score}/10</span>
                  </div>
                )}
              </button>
            )
          })}

          {allEvaled && (
            <div style={{ marginTop: 8, textAlign: 'center' }}>
              <ScoreRing score={parseFloat(avgScore) * 10} label="Session" size={80} />
              <p style={{ color: '#94a3b8', fontSize: 12, marginTop: 4 }}>Avg: {avgScore} / 10</p>
            </div>
          )}

          <Button variant="ghost" size="sm" onClick={reset} style={{ marginTop: 6 }}>
            <RotateCcw size={13} /> New Session
          </Button>
        </div>

        {/* Active question */}
        <Card className="space-y-5">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 10, flexWrap: 'wrap' }}>
                <Badge color={DIFF_COLOR[questions[activeIdx]?.difficulty]}>{questions[activeIdx]?.difficulty}</Badge>
                <Badge color={CAT_COLOR[questions[activeIdx]?.category]}>{questions[activeIdx]?.category}</Badge>
                <span style={{ fontSize: 11, color: '#64748b' }}>{activeIdx + 1} / {questions.length}</span>
              </div>
              <p style={{ color: 'white', fontWeight: 600, fontSize: 15, lineHeight: 1.6 }}>
                {questions[activeIdx]?.question}
              </p>
            </div>
            {evaluations[activeIdx] && (
              <ScoreRing score={evaluations[activeIdx].score * 10} label="Score" size={68} />
            )}
          </div>

          <Textarea label="Your Answer"
            placeholder="Write your answer here. Be detailed — include examples and explain your reasoning..."
            rows={9}
            value={answers[activeIdx] || ''}
            onChange={e => setAnswers(p => ({ ...p, [activeIdx]: e.target.value }))}
          />

          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
            <Button onClick={() => evaluate(activeIdx)} loading={loadingEval[activeIdx]}
              variant="success" disabled={!answers[activeIdx]?.trim()}>
              {loadingEval[activeIdx] ? 'Evaluating...' : 'Evaluate'}
              {!loadingEval[activeIdx] && <Brain size={16} />}
            </Button>
            {evaluations[activeIdx] && (
              <Button onClick={() => saveRecord(activeIdx)} loading={loadingSave[activeIdx]} variant="secondary">
                <Save size={15} /> Save
              </Button>
            )}
            <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
              <Button onClick={() => setActiveIdx(i => Math.max(i - 1, 0))}
                variant="ghost" size="sm" disabled={activeIdx === 0}>← Prev</Button>
              <Button onClick={() => setActiveIdx(i => Math.min(i + 1, questions.length - 1))}
                variant="ghost" size="sm" disabled={activeIdx === questions.length - 1}>Next →</Button>
            </div>
          </div>

          {evaluations[activeIdx] && <EvalResult ev={evaluations[activeIdx]} />}
        </Card>
      </div>
    </div>
  )
}

function EvalResult({ ev }) {
  return (
    <div style={{
      borderRadius: 12, padding: 16,
      background: 'rgba(99,102,241,0.06)',
      border: '1px solid rgba(99,102,241,0.2)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
        {correctIcon(ev.is_correct)}
        <span style={{ color: 'white', fontWeight: 600, fontSize: 14 }}>
          {ev.is_correct === 'yes' ? 'Correct' : ev.is_correct === 'partial' ? 'Partially Correct' : 'Needs Improvement'}
        </span>
        <span style={{ marginLeft: 'auto', color: '#818cf8', fontWeight: 700 }}>{ev.score} / 10</span>
      </div>
      <p style={{ color: '#cbd5e1', fontSize: 14, lineHeight: 1.6, marginBottom: 10 }}>{ev.feedback}</p>

      {ev.strengths?.length > 0 && (
        <div style={{ marginBottom: 10 }}>
          <p style={{ color: '#34d399', fontSize: 12, fontWeight: 600, marginBottom: 6 }}>Strengths</p>
          {ev.strengths.map((s, i) => (
            <div key={i} style={{ display: 'flex', gap: 6, marginBottom: 4 }}>
              <CheckCircle size={12} style={{ color: '#10b981', flexShrink: 0, marginTop: 2 }} />
              <span style={{ color: '#94a3b8', fontSize: 13 }}>{s}</span>
            </div>
          ))}
        </div>
      )}

      {ev.weaknesses?.length > 0 && (
        <div>
          <p style={{ color: '#fbbf24', fontSize: 12, fontWeight: 600, marginBottom: 6 }}>Areas to Improve</p>
          {ev.weaknesses.map((w, i) => (
            <div key={i} style={{ display: 'flex', gap: 6, marginBottom: 4 }}>
              <Minus size={12} style={{ color: '#f59e0b', flexShrink: 0, marginTop: 2 }} />
              <span style={{ color: '#94a3b8', fontSize: 13 }}>{w}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
