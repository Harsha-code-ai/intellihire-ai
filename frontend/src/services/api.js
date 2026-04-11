import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({ baseURL: BASE_URL })

// Inject auth token from localStorage/zustand persist
api.interceptors.request.use((config) => {
  try {
    const stored = JSON.parse(localStorage.getItem('intellihire-auth') || '{}')
    const token = stored?.state?.token
    if (token) config.headers.Authorization = `Bearer ${token}`
  } catch (_) {}
  return config
})

// ── Auth ──────────────────────────────────────────────────────────────────
export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  login:    (data) => api.post('/api/auth/login',    data),
  me:       ()     => api.get('/api/auth/me'),
}

// ── Resume ────────────────────────────────────────────────────────────────
export const resumeAPI = {
  upload: (file, jobRole, jobDescription) => {
    const form = new FormData()
    form.append('file', file)
    if (jobRole)        form.append('job_role', jobRole)
    if (jobDescription) form.append('job_description', jobDescription)
    return api.post('/api/resume/upload-resume', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  jobFit: (analysisId, jobRole, jobDescription) =>
    api.post('/api/resume/job-fit', null, {
      params: { analysis_id: analysisId, job_role: jobRole, job_description: jobDescription },
    }),
  history: () => api.get('/api/resume/history'),
  get:     (id) => api.get(`/api/resume/${id}`),
}

// ── Interview ─────────────────────────────────────────────────────────────
export const interviewAPI = {
  generateQuestions: (data) => api.post('/api/interview/generate-questions', data),
  evaluateAnswer:    (data) => api.post('/api/interview/evaluate-answer', data),
  save:              (data) => api.post('/api/interview/save', data),
  history:           ()     => api.get('/api/interview/history'),
  delete:            (id)   => api.delete(`/api/interview/${id}`),
}

export default api
