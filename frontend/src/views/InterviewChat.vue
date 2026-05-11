<template>
  <div class="chat-page">
    <!-- Top Bar -->
    <header class="chat-header">
      <div class="header-left">
        <router-link to="/" class="brand-mini">
          <span class="brand-icon-sm">◆</span>
        </router-link>
        <div class="session-info">
          <span class="session-title">{{ sessionInfo }}</span>
          <span v-if="isFollowUp" class="follow-up-badge">追问中</span>
        </div>
      </div>
      <div class="header-right">
        <button :class="['voice-toggle', { active: voiceEnabled }]" @click="toggleVoice" title="语音开关">
          <svg v-if="voiceEnabled" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 1v7M5 5l3 3 3-3"/><path d="M2 8a6 6 0 0012 0"/></svg>
          <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 1v7M5 5l3 3 3-3"/><path d="M2 8a6 6 0 0012 0"/><line x1="2" y1="2" x2="14" y2="14"/></svg>
          {{ voiceEnabled ? '语音开' : '语音关' }}
        </button>
        <button class="btn btn-secondary btn-sm pause-btn" @click="pauseInterview" title="暂停保存">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor"><rect x="3" y="2" width="4" height="12" rx="1"/><rect x="9" y="2" width="4" height="12" rx="1"/></svg>
          暂停保存
        </button>
        <button class="btn btn-danger btn-sm end-btn" @click="endInterview">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor"><rect x="3" y="3" width="10" height="10" rx="1"/></svg>
          结束面试
        </button>
      </div>
    </header>

    <!-- Status Bar -->
    <div class="status-bar">
      <div class="status-item">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="6"/><path d="M8 5v3l2 2"/></svg>
        <span>{{ formatTime(elapsed) }}</span>
      </div>
      <div class="status-item">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="12" height="12" rx="2"/><path d="M5 6h6M5 9h4"/></svg>
        <span>第 {{ currentQuestion }} / 8 题</span>
      </div>
      <div v-if="isFollowUp" class="status-item follow-up">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 8h12M8 2l6 6-6 6"/></svg>
        <span>追问 {{ followUpCount }}/3</span>
      </div>
    </div>

    <!-- Chat Area -->
    <div class="chat-area" ref="chatArea">
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        :class="['message', msg.role]"
      >
        <div class="msg-avatar">
          <div v-if="msg.role === 'ai'" class="avatar avatar-ai">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" fill="currentColor" opacity="0.9"/><path d="M4 20c0-3.3 3.6-6 8-6s8 2.7 8 6" fill="currentColor" opacity="0.7"/></svg>
          </div>
          <div v-else class="avatar avatar-user">我</div>
        </div>
        <div class="msg-body">
          <div class="msg-bubble">
            <p>{{ msg.content }}</p>
          </div>
          <span class="msg-time">{{ msg.time }}</span>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="input-area">
      <button
        :class="['mic-btn', { recording: isRecording }]"
        @click="startRecording"
        title="点击开始/停止语音输入"
      >
        <svg v-if="!isRecording" width="18" height="18" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 1a3 3 0 00-3 3v3a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M3 7a5 5 0 0010 0"/><line x1="8" y1="12" x2="8" y2="15"/></svg>
        <svg v-else width="18" height="18" viewBox="0 0 16 16" fill="currentColor"><rect x="3" y="3" width="10" height="10" rx="1"/></svg>
      </button>
      <div class="input-wrapper">
        <input
          v-model="inputMessage"
          :placeholder="recordingStatus || '输入你的回答...'"
          @keydown.enter="sendMessage"
          class="chat-input"
        />
        <span v-if="recordingStatus" class="recording-hint">{{ recordingStatus }}</span>
      </div>
      <button class="send-btn" @click="sendMessage" :disabled="!inputMessage.trim()">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 8l12-5-5 12-2-5-5-2z"/></svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useInterviewStore } from '../stores/interview.js'

const route = useRoute()
const router = useRouter()
const interviewStore = useInterviewStore()
const sessionId = route.params.sessionId

const messages = ref([])
const inputMessage = ref('')
const elapsed = ref(0)
const currentQuestion = ref(1)
const isFollowUp = ref(false)
const followUpCount = ref(1)
const chatArea = ref(null)
const sessionInfo = ref('加载中...')
const sessionData = ref(null)
const voiceEnabled = ref(true)
const isRecording = ref(false)
const recordingStatus = ref('')

let timer = null
let recognition = null
let audioPlayer = null
let recordTimeout = null

onMounted(async () => {
  timer = setInterval(() => elapsed.value++, 1000)
  try {
    const res = await fetch(`/api/sessions/${sessionId}`)
    if (res.ok) {
      sessionData.value = await res.json()
      // 恢复已用时间
      if (sessionData.value.elapsed_seconds) {
        elapsed.value = sessionData.value.elapsed_seconds
      }
      const profileRes = await fetch(`/api/profiles/${sessionData.value.profile_id}`)
      let company = ''
      let position = ''
      if (profileRes.ok) {
        const profile = await profileRes.json()
        company = profile.target_company
        position = profile.target_position
        const roundLabel = sessionData.value.interview_round === 'hr' ? 'HR面' : '业务面'
        sessionInfo.value = `${company} · ${position} · ${roundLabel}`
      }
      if (sessionData.value.conversation_history && sessionData.value.conversation_history.length > 0) {
        messages.value = sessionData.value.conversation_history.map(m => ({
          role: m.role,
          content: m.content,
          time: m.time || formatTimeNow(),
        }))
        // 正式题号 = AI消息中非追问消息的数量（追问包含"能否再详细展开一下"）
        const aiMsgs = messages.value.filter(m => m.role === 'ai')
        const followUpMsgs = aiMsgs.filter(m => m.content && m.content.includes('能否再详细展开一下'))
        currentQuestion.value = aiMsgs.length - followUpMsgs.length
        // 追问计数从1开始，已有追问时设为最新追问次数+1（下次追问显示的序号）
        const lastFollowUps = countTrailingFollowUps(aiMsgs)
        followUpCount.value = lastFollowUps > 0 ? lastFollowUps : 1
        isFollowUp.value = lastFollowUps > 0
      } else {
        const q1Res = await fetch(`/api/sessions/${sessionId}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: '（面试开始）' }),
        })
        const q1Data = await q1Res.json()
        messages.value.push({
          role: 'ai',
          content: q1Data.message,
          time: formatTimeNow(),
        })
        currentQuestion.value = 1
        if (voiceEnabled.value && q1Data.message) {
          setTimeout(() => playTTS(q1Data.message), 500)
        }
      }
    }
  } catch (err) {
    sessionInfo.value = '面试会话'
    messages.value.push({ role: 'ai', content: '你好，我是今天的面试官。请先做个自我介绍吧。', time: formatTimeNow() })
    currentQuestion.value = 1
  }
})

onUnmounted(() => {
  clearInterval(timer)
})

watch(() => messages.value.length, () => {
  nextTick(() => {
    chatArea.value?.scrollTo({ top: chatArea.value.scrollHeight, behavior: 'smooth' })
  })
})

function formatTime(seconds) {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0')
  const s = (seconds % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

function formatTimeNow() {
  const d = new Date()
  return `${d.getHours()}:${d.getMinutes().toString().padStart(2, '0')}`
}

/** 统计末尾连续追问消息数（从最后一条AI消息往前数连续追问） */
function countTrailingFollowUps(aiMsgs) {
  let count = 0
  for (let i = aiMsgs.length - 1; i >= 0; i--) {
    if (aiMsgs[i].content && aiMsgs[i].content.includes('能否再详细展开一下')) {
      count++
    } else {
      break
    }
  }
  return count
}

async function sendMessage() {
  const text = inputMessage.value.trim()
  if (!text) return

  messages.value.push({ role: 'user', content: text, time: formatTimeNow() })
  inputMessage.value = ''

  try {
    const res = await interviewStore.sendChat(sessionId, text)
    messages.value.push({ role: 'ai', content: res.message, time: formatTimeNow() })
    isFollowUp.value = res.is_follow_up
    // 后端 follow_up_count 从0开始，前端显示"第几次追问"需要+1
    // 追问时：显示当前追问序号；非追问时：重置为1（下次追问时从1开始）
    followUpCount.value = res.is_follow_up ? res.follow_up_count + 1 : 1
    if (!res.is_follow_up) currentQuestion.value++
    if (voiceEnabled.value) {
      await playTTS(res.message)
    }
  } catch (err) {
    messages.value.push({ role: 'ai', content: '（网络异常，请稍后重试）', time: formatTimeNow() })
  }
}

function toggleVoice() {
  voiceEnabled.value = !voiceEnabled.value
}

async function playTTS(text) {
  if (!text || text.length > 500) return
  try {
    if (audioPlayer) {
      audioPlayer.pause()
      audioPlayer = null
    }
    const res = await fetch('/api/voice/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, voice: 'zh-CN-XiaoxiaoNeural' }),
    })
    if (!res.ok) {
      const errText = await res.text().catch(() => 'unknown')
      console.error('TTS request failed:', res.status, errText)
      return
    }
    const blob = await res.blob()
    if (blob.size < 1000) {
      console.warn('TTS audio too small, possibly empty')
      return
    }
    const url = URL.createObjectURL(blob)
    audioPlayer = new Audio(url)
    const playPromise = audioPlayer.play()
    if (playPromise !== undefined) {
      playPromise.catch(err => {
        console.warn('Autoplay blocked, waiting for user interaction:', err)
      })
    }
  } catch (e) {
    console.error('TTS play failed:', e)
  }
}

function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) {
    console.warn('浏览器不支持语音识别')
    recordingStatus.value = '当前浏览器不支持语音输入'
    return null
  }
  const rec = new SpeechRecognition()
  rec.lang = 'zh-CN'
  rec.continuous = true
  rec.interimResults = true

  let finalTranscript = ''

  rec.onstart = () => {
    finalTranscript = ''
    recordingStatus.value = '正在聆听，请说话...'
    isRecording.value = true
  }

  rec.onresult = (event) => {
    let interimTranscript = ''
    let currentFinal = ''
    for (let i = 0; i < event.results.length; i++) {
      const result = event.results[i]
      const transcript = result[0].transcript
      if (result.isFinal) {
        currentFinal += transcript
      } else {
        interimTranscript += transcript
      }
    }
    finalTranscript = currentFinal
    const fullText = (finalTranscript + interimTranscript).trim()
    inputMessage.value = fullText
  }

  rec.onerror = (event) => {
    let errorMsg = '语音识别出错'
    if (event.error === 'not-allowed') errorMsg = '麦克风权限被拒绝'
    else if (event.error === 'no-speech') errorMsg = '没有检测到语音，请重试'
    else if (event.error === 'network') errorMsg = '网络错误'
    else if (event.error === 'aborted') errorMsg = '语音识别已中止'
    else errorMsg = '语音识别出错: ' + event.error
    recordingStatus.value = errorMsg
    isRecording.value = false
  }

  rec.onend = () => {
    isRecording.value = false
    recordingStatus.value = ''
  }

  return rec
}

async function startRecording() {
  if (isRecording.value) {
    stopRecording()
    return
  }

  if (recordTimeout) {
    clearTimeout(recordTimeout)
    recordTimeout = null
  }

  if (recognition) {
    try { recognition.abort() } catch (e) { /* ignore */ }
    recognition = null
  }
  recognition = initSpeechRecognition()

  if (!recognition) {
    alert('当前浏览器不支持语音输入，请使用 Chrome/Edge/Safari 浏览器')
    return
  }

  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const audioTrack = stream.getAudioTracks()[0]
      if (!audioTrack || !audioTrack.enabled) {
        recordingStatus.value = '麦克风未激活，请检查设备'
        return
      }
      try {
        recognition.start()
      } catch (e) {
        recordingStatus.value = '启动语音识别失败，请刷新页面重试'
        isRecording.value = false
        return
      }
      recordTimeout = setTimeout(() => {
        if (isRecording.value) stopRecording()
      }, 30000)
    } catch (err) {
      recordingStatus.value = '麦克风权限被拒绝，请手动输入'
      alert('无法访问麦克风，请检查浏览器权限设置')
    }
  } else {
    try {
      recognition.start()
    } catch (e) {
      recordingStatus.value = '启动语音识别失败'
      isRecording.value = false
      return
    }
    recordTimeout = setTimeout(() => {
      if (isRecording.value) stopRecording()
    }, 30000)
  }
}

function stopRecording() {
  if (recordTimeout) {
    clearTimeout(recordTimeout)
    recordTimeout = null
  }
  isRecording.value = false
  try { recognition?.stop() } catch (e) { /* ignore */ }
}

async function pauseInterview() {
  if (!confirm('确定要暂停面试吗？进度将自动保存，可从历史记录继续。')) return
  try {
    await fetch(`/api/sessions/${sessionId}/pause`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ elapsed_seconds: elapsed.value }),
    })
    router.push('/history')
  } catch (err) {
    alert('暂停失败: ' + err.message)
  }
}

async function endInterview() {
  if (!confirm('确定要结束面试吗？')) return
  try {
    await interviewStore.endSession(sessionId)
    router.push(`/report/${sessionId}`)
  } catch (err) {
    alert('结束面试失败: ' + err.message)
  }
}
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-subtle);
}

/* ── Header ── */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-5);
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-default);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.brand-mini {
  display: flex;
  align-items: center;
  text-decoration: none;
}

.brand-icon-sm {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-700));
  color: white;
  border-radius: var(--radius-sm);
  font-size: 11px;
}

.session-info {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.session-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.follow-up-badge {
  font-size: var(--text-xs);
  padding: 2px var(--space-2);
  background: var(--color-warning-50);
  color: var(--color-warning-600);
  border-radius: var(--radius-full);
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.voice-toggle {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-3);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  font-size: var(--text-xs);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.voice-toggle:hover {
  border-color: var(--color-primary-300);
  color: var(--color-primary-600);
}

.voice-toggle.active {
  background: var(--color-primary-50);
  border-color: var(--color-primary-300);
  color: var(--color-primary-700);
}

.btn-sm {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
  border-radius: var(--radius-md);
}

.end-btn {
  border-radius: var(--radius-md);
}

.pause-btn {
  border-radius: var(--radius-md);
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* ── Status Bar ── */
.status-bar {
  display: flex;
  align-items: center;
  gap: var(--space-6);
  padding: var(--space-2) var(--space-5);
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-light);
  flex-shrink: 0;
}

.status-item {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  color: var(--text-muted);
  font-weight: 500;
}

.status-item.follow-up {
  color: var(--color-warning-600);
}

/* ── Chat Area ── */
.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.message {
  display: flex;
  gap: var(--space-3);
  max-width: 80%;
}

.message.ai {
  align-self: flex-start;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.msg-avatar {
  flex-shrink: 0;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xs);
  font-weight: 600;
  flex-shrink: 0;
}

.avatar-ai {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.avatar-user {
  background: var(--color-gray-200);
  color: var(--text-secondary);
}

.msg-body {
  display: flex;
  flex-direction: column;
}

.message.user .msg-body {
  align-items: flex-end;
}

.msg-bubble {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  box-shadow: var(--shadow-xs);
}

.message.ai .msg-bubble {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-top-left-radius: var(--radius-sm);
}

.message.user .msg-bubble {
  background: var(--color-primary-600);
  color: white;
  border-top-right-radius: var(--radius-sm);
}

.msg-bubble p {
  margin: 0;
}

.msg-time {
  font-size: 11px;
  color: var(--text-faint);
  margin-top: var(--space-1);
  padding: 0 var(--space-1);
}

/* ── Input Area ── */
.input-area {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-5);
  background: var(--bg-surface);
  border-top: 1px solid var(--border-default);
  flex-shrink: 0;
}

.mic-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid var(--border-default);
  border-radius: 50%;
  background: var(--bg-surface);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.mic-btn:hover {
  border-color: var(--color-primary-300);
  color: var(--color-primary-600);
}

.mic-btn.recording {
  background: var(--color-error-600);
  border-color: var(--color-error-600);
  color: white;
  animation: breathe 1.5s ease-in-out infinite;
}

.input-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
}

.chat-input {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  background: var(--bg-muted);
  font-size: var(--text-sm);
  transition: all var(--transition-fast);
  outline: none;
}

.chat-input:focus {
  border-color: var(--color-primary-400);
  background: var(--bg-surface);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.08);
}

.recording-hint {
  font-size: var(--text-xs);
  color: var(--color-error-600);
  margin-top: var(--space-1);
  padding-left: var(--space-1);
}

.send-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: var(--color-primary-600);
  color: white;
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: var(--color-primary-700);
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
