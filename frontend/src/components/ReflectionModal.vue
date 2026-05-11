<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal animate-slide-up">
      <header class="modal-header">
        <div class="modal-title-group">
          <svg width="20" height="20" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 4h12v8a2 2 0 01-2 2H4a2 2 0 01-2-2V4zM2 4l2-2h8l2 2"/></svg>
          <h3>面试反思总结</h3>
        </div>
        <button class="btn btn-ghost modal-close" @click="$emit('close')">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 4l8 8M12 4l-8 8"/></svg>
        </button>
      </header>

      <div class="modal-body">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>正在加载...</p>
        </div>
        <div v-else-if="error" class="error-state">{{ error }}</div>

        <!-- AI Reflection -->
        <div v-if="reflection.reflection_summary" class="section">
          <h4 class="section-label">AI 反思总结</h4>
          <div class="reflection-content markdown" v-html="formatMarkdown(reflection.reflection_summary)"></div>
        </div>
        <div v-else class="section generate-section">
          <button class="btn btn-primary" @click="generateReflection" :disabled="generating">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 1l2 5h5l-4 3 1.5 5L8 11 3.5 14 5 9 1 6h5z"/></svg>
            {{ generating ? '生成中...' : '生成 AI 反思总结' }}
          </button>
        </div>

        <!-- Conversation History -->
        <div class="section">
          <h4 class="section-label">对话记录</h4>
          <div class="history-list">
            <div
              v-for="(msg, idx) in conversationHistory"
              :key="idx"
              :class="['history-item', msg.role]"
            >
              <div class="history-item-header">
                <span class="role-badge" :class="msg.role">
                  {{ msg.role === 'ai' ? '面试官' : '我' }}
                </span>
                <button
                  class="star-btn"
                  :class="{ starred: isStarred(idx) }"
                  @click="toggleStar(idx)"
                  title="标记为重点题"
                >
                  {{ isStarred(idx) ? '★' : '☆' }}
                </button>
              </div>
              <p class="history-item-content">{{ msg.content }}</p>
              <!-- Notes for AI questions -->
              <div v-if="msg.role === 'ai'" class="note-area">
                <textarea
                  :value="getNote(idx)"
                  @input="updateNote(idx, $event.target.value)"
                  placeholder="写下你的复盘笔记..."
                  rows="2"
                  class="form-input"
                ></textarea>
              </div>
            </div>
          </div>
        </div>
      </div>

      <footer class="modal-footer">
        <button class="btn btn-ghost" @click="$emit('close')">关闭</button>
        <button class="btn btn-primary" @click="saveNotes">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 3h12v10a1 1 0 01-1 1H3a1 1 0 01-1-1V3zM2 3l2-2h8l2 2"/><path d="M6 6h4"/></svg>
          保存笔记
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({ sessionId: String })
const emit = defineEmits(['close'])

const loading = ref(true)
const error = ref('')
const reflection = ref({})
const conversationHistory = ref([])
const starredIndices = ref([])
const notes = ref({})
const generating = ref(false)

onMounted(async () => {
  await loadReflection()
})

async function loadReflection() {
  try {
    const res = await fetch(`/api/sessions/${props.sessionId}/reflection`)
    if (!res.ok) throw new Error('加载失败')
    const data = await res.json()
    reflection.value = data
    conversationHistory.value = data.conversation_history || []
    starredIndices.value = data.starred_questions || []
    notes.value = data.reflection_notes || {}
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function generateReflection() {
  generating.value = true
  try {
    const res = await fetch(`/api/sessions/${props.sessionId}/reflection/generate`, { method: 'POST' })
    if (!res.ok) throw new Error('生成失败')
    const data = await res.json()
    reflection.value.reflection_summary = data.reflection_summary
  } catch (err) {
    error.value = err.message
  } finally {
    generating.value = false
  }
}

function isStarred(idx) {
  return starredIndices.value.includes(idx)
}

function toggleStar(idx) {
  if (isStarred(idx)) {
    starredIndices.value = starredIndices.value.filter(i => i !== idx)
  } else {
    starredIndices.value.push(idx)
  }
}

function getNote(idx) {
  return notes.value[idx] || ''
}

function updateNote(idx, text) {
  notes.value[idx] = text
}

async function saveNotes() {
  try {
    await fetch(`/api/sessions/${props.sessionId}/reflection/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notes: notes.value }),
    })
    await fetch(`/api/sessions/${props.sessionId}/reflection/stars`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ indices: starredIndices.value }),
    })
    alert('笔记已保存')
  } catch (err) {
    alert('保存失败: ' + err.message)
  }
}

function formatMarkdown(text) {
  if (!text) return ''
  return text
    .replace(/### (.*)/g, '<h5>$1</h5>')
    .replace(/## (.*)/g, '<h4>$1</h4>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
}

.modal {
  background: var(--bg-surface);
  border-radius: var(--radius-xl);
  width: 90%;
  max-width: 720px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-xl);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border-light);
}

.modal-title-group {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--text-primary);
}

.modal-title-group h3 {
  font-size: var(--text-md);
  font-weight: 600;
  margin: 0;
}

.modal-close {
  padding: var(--space-1);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
}

/* ── Loading / Error ── */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-8);
  color: var(--text-muted);
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid var(--color-gray-200);
  border-top-color: var(--color-primary-500);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.error-state {
  text-align: center;
  padding: var(--space-6);
  color: var(--color-error-500);
}

/* ── Section ── */
.section {
  margin-bottom: var(--space-6);
}

.section-label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-3);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.generate-section {
  display: flex;
  justify-content: center;
  padding: var(--space-6);
  background: var(--bg-muted);
  border-radius: var(--radius-lg);
}

/* ── Reflection Content ── */
.reflection-content {
  background: var(--bg-muted);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
}

.reflection-content :deep(h4) {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
  margin: var(--space-3) 0 var(--space-2);
}

.reflection-content :deep(h5) {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
  margin: var(--space-2) 0 var(--space-1);
}

.reflection-content :deep(strong) {
  color: var(--text-primary);
}

/* ── History List ── */
.history-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.history-item {
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: var(--space-3);
}

.history-item.ai {
  background: var(--color-primary-50);
  border-color: var(--color-primary-100);
}

.history-item.user {
  background: var(--bg-muted);
}

.history-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-2);
}

.role-badge {
  display: inline-flex;
  padding: 2px var(--space-2);
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 600;
}

.role-badge.ai {
  background: var(--color-primary-100);
  color: var(--color-primary-700);
}

.role-badge.user {
  background: var(--color-gray-200);
  color: var(--text-secondary);
}

.star-btn {
  background: none;
  border: none;
  font-size: var(--text-md);
  cursor: pointer;
  color: var(--color-gray-300);
  transition: color var(--transition-fast);
  padding: 0;
}

.star-btn.starred {
  color: #f59e0b;
}

.star-btn:hover {
  color: #f59e0b;
}

.history-item-content {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
  margin: 0;
}

.note-area {
  margin-top: var(--space-2);
}

.note-area textarea {
  font-size: var(--text-sm);
  resize: vertical;
}

/* ── Modal Footer ── */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--border-light);
}
</style>
