<template>
  <AppLayout>
    <div class="history-container">
      <!-- Page Header -->
      <div class="page-header">
        <router-link to="/" class="back-link">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10 3L5 8l5 5"/></svg>
          返回首页
        </router-link>
        <h1 class="page-title">面试历史</h1>
      </div>

      <!-- Filters -->
      <div class="filters">
        <button
          v-for="f in filters"
          :key="f.value"
          :class="['filter-btn', { active: activeFilter === f.value }]"
          @click="activeFilter = f.value"
        >
          {{ f.label }}
        </button>
      </div>

      <!-- Session List -->
      <div class="session-list">
        <div
          v-for="s in filteredSessions"
          :key="s.session_id"
          :class="['session-card', `status-${s.status}`]"
        >
          <div class="session-indicator" :class="s.status"></div>
          <div class="session-content">
            <div class="session-top">
              <h4 class="session-name">{{ sessionTitle(s) }}</h4>
              <span :class="['status-badge', s.status]">
                {{ s.status === 'completed' ? '已完成' : s.status === 'paused' ? '已暂停' : '进行中' }}
              </span>
            </div>
            <div class="session-meta">
              <span class="meta-item">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="6"/><path d="M8 5v3l2 2"/></svg>
                {{ formatDate(s.started_at) }}
              </span>
              <span v-if="s.total_score" class="meta-item score">
                {{ s.total_score }} 分
              </span>
            </div>
          </div>
          <div class="session-actions">
            <button v-if="s.status !== 'completed'" class="btn btn-primary btn-sm" @click="resumeSession(s.session_id)">
              <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor"><path d="M4 2l10 6-10 6V2z"/></svg>
              继续
            </button>
            <template v-else>
              <button class="btn btn-ghost btn-sm" @click="openReflection(s.session_id)">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 4h12v8a2 2 0 01-2 2H4a2 2 0 01-2-2V4zM2 4l2-2h8l2 2"/></svg>
                反思
              </button>
              <button class="btn btn-secondary btn-sm" @click="viewReport(s.session_id)">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 2h12v12H2z"/><path d="M5 6h6M5 9h4"/></svg>
                报告
              </button>
            </template>
            <button class="btn btn-ghost btn-sm btn-delete-action" @click="deleteSession(s.session_id, sessionTitle(s))" title="删除">
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 4h12M5 4V3a1 1 0 011-1h4a1 1 0 011 1v1M6 7v5M10 7v5M3 4l1 9a1 1 0 001 1h6a1 1 0 001-1l1-9"/></svg>
            </button>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="filteredSessions.length === 0 && !interviewStore.loading" class="empty-state">
          <div class="empty-state-icon">
            <svg width="40" height="40" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1"><circle cx="8" cy="8" r="6"/><path d="M8 5v3l2 2"/></svg>
          </div>
          <p class="empty-state-text">暂无面试记录</p>
          <router-link to="/" class="btn btn-primary btn-sm" style="margin-top: 12px;">开始第一次面试</router-link>
        </div>
      </div>

      <!-- Reflection Modal -->
      <ReflectionModal
        v-if="reflectionSessionId"
        :session-id="reflectionSessionId"
        @close="reflectionSessionId = null"
      />
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useInterviewStore } from '../stores/interview.js'
import AppLayout from '../components/AppLayout.vue'
import ReflectionModal from '../components/ReflectionModal.vue'

const router = useRouter()
const interviewStore = useInterviewStore()

const activeFilter = ref('all')
const filters = [
  { value: 'all', label: '全部' },
  { value: 'in_progress', label: '进行中' },
  { value: 'paused', label: '已暂停' },
  { value: 'completed', label: '已完成' },
]
const reflectionSessionId = ref(null)

onMounted(() => {
  interviewStore.fetchSessions()
})

const filteredSessions = computed(() => {
  if (activeFilter.value === 'all') return interviewStore.sessions
  return interviewStore.sessions.filter(s => s.status === activeFilter.value)
})

function sessionTitle(s) {
  const company = s.target_company || '未知公司'
  const position = s.target_position || ''
  const roundLabel = s.interview_round === 'hr' ? 'HR面' : '业务面'
  return position ? `${company} · ${position} · ${roundLabel}` : `${company} · ${roundLabel}`
}

function formatDate(dateStr) {
  if (!dateStr) return '未知日期'
  const d = new Date(dateStr)
  const y = d.getFullYear()
  const m = (d.getMonth() + 1).toString().padStart(2, '0')
  const day = d.getDate().toString().padStart(2, '0')
  return `${y}-${m}-${day}`
}

function resumeSession(sessionId) {
  router.push(`/interview/${sessionId}`)
}

function viewReport(sessionId) {
  router.push(`/report/${sessionId}`)
}

function openReflection(sessionId) {
  reflectionSessionId.value = sessionId
}

async function deleteSession(sessionId, title) {
  if (!confirm(`确定要删除面试记录「${title}」吗？此操作不可恢复。`)) return
  try {
    const res = await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('删除失败')
    interviewStore.sessions = interviewStore.sessions.filter(s => s.session_id !== sessionId)
  } catch (err) {
    alert('删除失败: ' + err.message)
  }
}
</script>

<style scoped>
.history-container {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--space-8) var(--space-6) var(--space-16);
}

/* ── Page Header ── */
.page-header {
  margin-bottom: var(--space-6);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-sm);
  color: var(--text-muted);
  margin-bottom: var(--space-3);
  transition: color var(--transition-fast);
}
.back-link:hover {
  color: var(--color-primary-600);
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

/* ── Filters ── */
.filters {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-6);
}

.filter-btn {
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  background: var(--bg-surface);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-btn:hover {
  border-color: var(--color-primary-300);
  color: var(--color-primary-600);
}

.filter-btn.active {
  background: var(--color-primary-600);
  border-color: var(--color-primary-600);
  color: white;
}

/* ── Session List ── */
.session-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.session-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs);
  transition: all var(--transition-fast);
}

.session-card:hover {
  box-shadow: var(--shadow-sm);
  border-color: var(--color-primary-200);
}

.session-indicator {
  width: 4px;
  height: 40px;
  border-radius: 2px;
  flex-shrink: 0;
}

.session-indicator.completed { background: var(--color-success-500); }
.session-indicator.in_progress { background: var(--color-primary-500); }
.session-indicator.paused { background: var(--color-warning-500); }

.session-content {
  flex: 1;
  min-width: 0;
}

.session-top {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-1);
}

.session-name {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-badge {
  padding: 2px var(--space-2);
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 500;
  flex-shrink: 0;
}

.status-badge.completed {
  background: var(--color-success-50);
  color: var(--color-success-600);
}

.status-badge.in_progress {
  background: var(--color-primary-50);
  color: var(--color-primary-700);
}

.status-badge.paused {
  background: var(--color-warning-50);
  color: var(--color-warning-600);
}

.session-meta {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.meta-item.score {
  font-weight: 600;
  color: var(--color-primary-600);
}

/* ── Session Actions ── */
.session-actions {
  display: flex;
  gap: var(--space-2);
  flex-shrink: 0;
}

.btn-sm {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
  gap: var(--space-1);
}

.btn-delete-action {
  color: var(--text-faint);
}

.btn-delete-action:hover {
  color: var(--color-danger-600);
  background: var(--color-danger-50);
}
</style>
