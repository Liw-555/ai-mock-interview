import { defineStore } from 'pinia'
import { ref } from 'vue'

const API_BASE = '/api'

export const useInterviewStore = defineStore('interview', () => {
  const sessions = ref([])
  const currentSession = ref(null)
  const loading = ref(false)

  async function fetchSessions(status = null) {
    loading.value = true
    try {
      const url = status ? `${API_BASE}/sessions?status=${status}` : `${API_BASE}/sessions`
      const res = await fetch(url)
      sessions.value = await res.json()
    } finally {
      loading.value = false
    }
  }

  async function createSession(data) {
    const res = await fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    const session = await res.json()
    currentSession.value = session
    return session
  }

  async function sendChat(sessionId, message) {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    })
    return await res.json()
  }

  async function endSession(sessionId) {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/end`, { method: 'POST' })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: '结束面试失败' }))
      throw new Error(err.detail || '结束面试失败')
    }
    return await res.json()
  }

  async function getReport(sessionId) {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/report`)
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: '加载报告失败' }))
      throw new Error(err.detail || '加载报告失败')
    }
    return await res.json()
  }

  return { sessions, currentSession, loading, fetchSessions, createSession, sendChat, endSession, getReport }
})
