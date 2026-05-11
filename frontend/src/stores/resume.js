import { defineStore } from 'pinia'
import { ref } from 'vue'

const API_BASE = '/api'

export const useResumeStore = defineStore('resume', () => {
  const resumes = ref([])
  const loading = ref(false)

  async function fetchResumes() {
    loading.value = true
    try {
      const res = await fetch(`${API_BASE}/resumes`)
      resumes.value = await res.json()
    } finally {
      loading.value = false
    }
  }

  async function uploadResume(file) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(`${API_BASE}/resumes/upload`, {
      method: 'POST',
      body: formData,
    })
    const text = await res.text()
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${text || 'Server error'}`)
    }
    let data
    try {
      data = JSON.parse(text)
    } catch {
      throw new Error(`Unexpected response: ${text.slice(0, 200)}`)
    }
    resumes.value.unshift(data)
    return data
  }

  async function deleteResume(resumeId) {
    await fetch(`${API_BASE}/resumes/${resumeId}`, { method: 'DELETE' })
    resumes.value = resumes.value.filter(r => r.resume_id !== resumeId)
  }

  return { resumes, loading, fetchResumes, uploadResume, deleteResume }
})
