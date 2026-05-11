<template>
  <AppLayout>
    <div class="config-container">
      <!-- Page Header -->
      <div class="page-header">
        <router-link to="/" class="back-link">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10 3L5 8l5 5"/></svg>
          返回首页
        </router-link>
        <h1 class="page-title">面试配置</h1>
        <p class="page-desc">完成以下配置后开始 AI 模拟面试</p>
      </div>

      <!-- Steps Progress -->
      <div class="steps-progress">
        <div
          v-for="(step, idx) in stepLabels"
          :key="idx"
          :class="['step-dot', { active: currentStep >= idx, current: currentStep === idx }]"
        >
          <span class="step-num">{{ idx + 1 }}</span>
          <span class="step-label">{{ step }}</span>
        </div>
        <div class="step-line">
          <div class="step-line-fill" :style="{ width: ((currentStep) / 3 * 100) + '%' }"></div>
        </div>
      </div>

      <!-- Step 1: Select Resume -->
      <section v-if="currentStep === 0" class="step-section animate-fade-in">
        <h3 class="section-title">选择简历</h3>
        <p class="section-subtitle">选择一份已上传的简历作为面试基础</p>
        <div class="select-grid">
          <div
            v-for="r in resumeStore.resumes"
            :key="r.resume_id"
            :class="['select-card', { selected: selectedResume === r.resume_id }]"
            @click="selectResume(r.resume_id)"
          >
            <div class="select-card-icon">
              <svg width="24" height="24" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.2"><path d="M4 2h5l3 3v9a1 1 0 01-1 1H4a1 1 0 01-1-1V3a1 1 0 011-1z"/><path d="M9 2v3h3"/></svg>
            </div>
            <div class="select-card-info">
              <span class="select-card-name">{{ r.original_filename || r.file_path.split(/[/\\]/).pop() }}</span>
              <span :class="['select-card-status', r.parsed_at ? 'ok' : 'pending']">
                {{ r.parsed_at ? '已解析' : '解析中' }}
              </span>
            </div>
            <div v-if="selectedResume === r.resume_id" class="select-check">
              <svg width="18" height="18" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 8l3 3 7-7"/></svg>
            </div>
          </div>
        </div>
        <div class="step-actions">
          <router-link to="/" class="btn btn-secondary">返回</router-link>
          <button class="btn btn-primary" :disabled="!selectedResume" @click="currentStep = 1">下一步</button>
        </div>
      </section>

      <!-- Step 2: Select Profile -->
      <section v-if="currentStep === 1" class="step-section animate-fade-in">
        <h3 class="section-title">选择岗位资料</h3>
        <p class="section-subtitle">选择目标公司和岗位，AI 将据此定制面试问题</p>
        <div class="select-grid">
          <div
            v-for="p in profiles"
            :key="p.profile_id"
            :class="['select-card', { selected: selectedProfile === p.profile_id }]"
            @click="selectedProfile = p.profile_id"
          >
            <div class="select-card-icon profile-icon">
              <svg width="24" height="24" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.2"><rect x="2" y="2" width="12" height="12" rx="2"/><path d="M5 6h6M5 9h4"/></svg>
            </div>
            <div class="select-card-info">
              <span class="select-card-name">{{ p.target_company }}</span>
              <span class="select-card-sub">{{ p.target_position }}</span>
            </div>
            <div class="select-card-actions">
              <button class="btn-icon-sm" @click.stop="openEditModal(p)" title="编辑">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M11.5 1.5l3 3L5 14H2v-3L11.5 1.5z"/></svg>
              </button>
              <div v-if="selectedProfile === p.profile_id" class="select-check">
                <svg width="18" height="18" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 8l3 3 7-7"/></svg>
              </div>
            </div>
          </div>
        </div>
        <button class="btn btn-ghost item-add-btn" @click="showProfileModal = true">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 3v10M3 8h10"/></svg>
          新建岗位资料
        </button>
        <div class="step-actions">
          <button class="btn btn-secondary" @click="currentStep = 0">上一步</button>
          <button class="btn btn-primary" :disabled="!selectedProfile" @click="currentStep = 2">下一步</button>
        </div>
      </section>

      <!-- Step 3: Round & Style -->
      <section v-if="currentStep === 2" class="step-section animate-fade-in">
        <div class="config-group">
          <h3 class="section-title">面试轮次</h3>
          <p class="section-subtitle">选择你要模拟的面试轮次</p>
          <div class="tag-group">
            <button
              v-for="round in rounds"
              :key="round.value"
              :class="['tag', { 'tag-active': selectedRound === round.value }]"
              @click="selectedRound = round.value"
            >
              {{ round.label }}
            </button>
          </div>
        </div>

        <div class="config-group">
          <h3 class="section-title">面试官风格</h3>
          <p class="section-subtitle">选择你希望模拟的面试氛围</p>
          <div class="style-cards">
            <div
              v-for="s in styles"
              :key="s.value"
              :class="['style-card', { selected: selectedStyle === s.value }]"
              @click="selectedStyle = s.value"
            >
              <span class="style-emoji">{{ s.emoji }}</span>
              <span class="style-label">{{ s.label }}</span>
              <span class="style-desc">{{ s.desc }}</span>
            </div>
          </div>
        </div>

        <div class="step-actions">
          <button class="btn btn-secondary" @click="currentStep = 1">上一步</button>
          <button class="btn btn-primary" @click="currentStep = 3">预览确认</button>
        </div>
      </section>

      <!-- Step 4: Preview & Start -->
      <section v-if="currentStep === 3" class="step-section animate-fade-in">
        <h3 class="section-title">面试预览</h3>
        <div class="preview-card">
          <div class="preview-row">
            <span class="preview-label">简历</span>
            <span class="preview-value">{{ selectedResumeName }}</span>
          </div>
          <div class="preview-row">
            <span class="preview-label">岗位</span>
            <span class="preview-value">{{ selectedProfileName }}</span>
          </div>
          <div class="preview-row">
            <span class="preview-label">轮次</span>
            <span class="preview-value">{{ selectedRoundLabel }}</span>
          </div>
          <div class="preview-row">
            <span class="preview-label">风格</span>
            <span class="preview-value">{{ selectedStyleLabel }}</span>
          </div>
          <div class="preview-row">
            <span class="preview-label">预计时长</span>
            <span class="preview-value">20 - 40 分钟</span>
          </div>
        </div>
        <div class="step-actions">
          <button class="btn btn-secondary" @click="currentStep = 2">返回修改</button>
          <button class="btn btn-primary btn-lg" :disabled="!canStart" @click="startInterview">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M4 2l10 6-10 6V2z"/></svg>
            开始面试
          </button>
        </div>
      </section>

      <!-- Profile Modal (Create / Edit) -->
      <div v-if="showProfileModal" class="modal-overlay" @click.self="closeProfileModal">
        <div class="modal animate-slide-up">
          <div class="modal-header">
            <h3>{{ editingProfileId ? '编辑岗位资料' : '新建岗位资料' }}</h3>
            <button class="btn btn-ghost modal-close" @click="closeProfileModal">✕</button>
          </div>
          <div class="modal-body">
            <label class="form-label">目标公司</label>
            <input v-model="newProfile.company" class="form-input" placeholder="例如：字节跳动" />
            <label class="form-label">目标岗位</label>
            <input v-model="newProfile.position" class="form-input" placeholder="例如：产品经理" />
            <label class="form-label">岗位 JD</label>
            <textarea v-model="newProfile.jd" class="form-input" placeholder="粘贴岗位描述..." rows="5"></textarea>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeProfileModal">取消</button>
            <button class="btn btn-primary" @click="editingProfileId ? updateProfileInConfig() : createProfile()">
              {{ editingProfileId ? '保存修改' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useResumeStore } from '../stores/resume.js'
import { useInterviewStore } from '../stores/interview.js'
import AppLayout from '../components/AppLayout.vue'

const route = useRoute()
const router = useRouter()
const resumeStore = useResumeStore()
const interviewStore = useInterviewStore()

const currentStep = ref(0)
const selectedResume = ref(route.query.resume_id || '')
const selectedProfile = ref(route.query.profile_id || '')
const selectedRound = ref('first')
const selectedStyle = ref('professional')
const showProfileModal = ref(false)
const editingProfileId = ref(null)
const profiles = ref([])

const stepLabels = ['选择简历', '选择岗位', '面试设置', '预览确认']

const rounds = [
  { value: 'first', label: '一面（业务）' },
  { value: 'second', label: '二面（管理）' },
  { value: 'hr', label: 'HR 面' },
]

const styles = [
  { value: 'professional', label: '专业严谨', emoji: '💼', desc: '严格按照面试流程，侧重专业能力考察' },
  { value: 'gentle', label: '温和引导', emoji: '🤝', desc: '鼓励式提问，帮助你发挥最佳水平' },
  { value: 'pressure', label: '压力面试', emoji: '🔥', desc: '高强度追问，检验应变和抗压能力' },
]

const newProfile = ref({ company: '', position: '', jd: '' })

onMounted(async () => {
  resumeStore.fetchResumes()
  await fetchProfiles()
  // Auto-advance if resume is pre-selected
  if (selectedResume.value) {
    currentStep.value = selectedProfile.value ? 2 : 1
  }
})

async function fetchProfiles() {
  const res = await fetch('/api/profiles')
  if (res.ok) {
    profiles.value = await res.json()
  }
}

function selectResume(id) {
  selectedResume.value = id
}

const selectedResumeName = computed(() => {
  const r = resumeStore.resumes.find(x => x.resume_id === selectedResume.value)
  return r ? (r.original_filename || r.file_path.split(/[/\\]/).pop()) : ''
})

const selectedProfileName = computed(() => {
  const p = profiles.value.find(x => x.profile_id === selectedProfile.value)
  return p ? `${p.target_company} - ${p.target_position}` : ''
})

const selectedRoundLabel = computed(() => rounds.find(r => r.value === selectedRound.value)?.label)
const selectedStyleLabel = computed(() => styles.find(s => s.value === selectedStyle.value)?.label)

const canStart = computed(() => selectedResume.value && selectedProfile.value && selectedRound.value)

async function startInterview() {
  const session = await interviewStore.createSession({
    resume_id: selectedResume.value,
    profile_id: selectedProfile.value,
    interview_round: selectedRound.value,
    interviewer_role: selectedRound.value === 'hr' ? 'hr' : 'business',
    interviewer_style: selectedStyle.value,
  })
  router.push(`/interview/${session.session_id}`)
}

function closeProfileModal() {
  showProfileModal.value = false
  editingProfileId.value = null
  newProfile.value = { company: '', position: '', jd: '' }
}

function openEditModal(profile) {
  editingProfileId.value = profile.profile_id
  newProfile.value = {
    company: profile.target_company,
    position: profile.target_position,
    jd: profile.job_description || '',
  }
  showProfileModal.value = true
}

async function createProfile() {
  if (!newProfile.value.company || !newProfile.value.position || !newProfile.value.jd) {
    alert('请填写完整信息')
    return
  }
  const res = await fetch('/api/profiles', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      target_company: newProfile.value.company,
      target_position: newProfile.value.position,
      job_description: newProfile.value.jd,
    }),
  })
  if (!res.ok) {
    const err = await res.text()
    alert('保存失败: ' + err)
    return
  }
  const profile = await res.json()
  profiles.value.unshift(profile)
  selectedProfile.value = profile.profile_id
  closeProfileModal()
}

async function updateProfileInConfig() {
  if (!newProfile.value.company || !newProfile.value.position) {
    alert('请至少填写目标公司和目标岗位')
    return
  }
  try {
    const res = await fetch(`/api/profiles/${editingProfileId.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_company: newProfile.value.company,
        target_position: newProfile.value.position,
        job_description: newProfile.value.jd || '暂无JD',
      }),
    })
    if (!res.ok) throw new Error('更新失败')
    const updated = await res.json()
    const idx = profiles.value.findIndex(p => p.profile_id === editingProfileId.value)
    if (idx !== -1) profiles.value[idx] = updated
    closeProfileModal()
  } catch (err) {
    alert('更新失败: ' + err.message)
  }
}
</script>

<style scoped>
.config-container {
  max-width: 720px;
  margin: 0 auto;
  padding: var(--space-8) var(--space-6) var(--space-16);
}

/* ── Page Header ── */
.page-header {
  margin-bottom: var(--space-8);
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

.page-desc {
  font-size: var(--text-sm);
  color: var(--text-muted);
  margin-top: var(--space-1);
}

/* ── Steps Progress ── */
.steps-progress {
  position: relative;
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--space-10);
  padding: 0 var(--space-4);
}

.step-dot {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  z-index: 1;
}

.step-num {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: var(--text-sm);
  font-weight: 600;
  background: var(--color-gray-100);
  color: var(--text-muted);
  transition: all var(--transition-normal);
}

.step-dot.active .step-num {
  background: var(--color-primary-600);
  color: white;
}

.step-dot.current .step-num {
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2);
}

.step-label {
  font-size: var(--text-xs);
  color: var(--text-faint);
  font-weight: 500;
}

.step-dot.active .step-label {
  color: var(--color-primary-700);
}

.step-line {
  position: absolute;
  top: 16px;
  left: 48px;
  right: 48px;
  height: 2px;
  background: var(--color-gray-200);
}

.step-line-fill {
  height: 100%;
  background: var(--color-primary-500);
  border-radius: 1px;
  transition: width var(--transition-slow);
}

/* ── Step Section ── */
.step-section {
  animation: fadeIn 0.3s ease-out;
}

.config-group {
  margin-bottom: var(--space-8);
}

/* ── Select Grid ── */
.select-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--space-3);
  margin-top: var(--space-4);
}

.select-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  background: var(--bg-surface);
}

.select-card:hover {
  border-color: var(--color-primary-300);
  background: var(--color-primary-50);
}

.select-card.selected {
  border-color: var(--color-primary-400);
  background: var(--color-primary-50);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.select-card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--color-gray-100);
  color: var(--text-muted);
  flex-shrink: 0;
}

.select-card.selected .select-card-icon {
  background: var(--color-primary-100);
  color: var(--color-primary-600);
}

.profile-icon {
  background: var(--color-primary-50) !important;
  color: var(--color-primary-500) !important;
}

.select-card-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.select-card-name {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.select-card-sub {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.select-card-status {
  font-size: var(--text-xs);
  font-weight: 500;
}
.select-card-status.ok { color: var(--color-success-600); }
.select-card-status.pending { color: var(--color-warning-600); }

.select-check {
  position: absolute;
  top: var(--space-2);
  right: var(--space-2);
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary-600);
  color: white;
  border-radius: 50%;
}

.select-card-actions {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  margin-left: auto;
  flex-shrink: 0;
}

.btn-icon-sm {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  cursor: pointer;
  color: var(--text-faint);
  transition: all var(--transition-fast);
  opacity: 0;
}

.select-card:hover .btn-icon-sm {
  opacity: 1;
}

.btn-icon-sm:hover {
  background: var(--color-primary-50);
  color: var(--color-primary-600);
}

/* ── Style Cards ── */
.style-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
  margin-top: var(--space-4);
}

.style-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-6) var(--space-4);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: center;
}

.style-card:hover {
  border-color: var(--color-primary-300);
}

.style-card.selected {
  border-color: var(--color-primary-400);
  background: var(--color-primary-50);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.style-emoji {
  font-size: 1.75rem;
}

.style-label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.style-desc {
  font-size: var(--text-xs);
  color: var(--text-muted);
  line-height: var(--leading-relaxed);
}

/* ── Item Add Button ── */
.item-add-btn {
  margin-top: var(--space-3);
  width: 100%;
  justify-content: center;
  border: 1px dashed var(--border-default);
  padding: var(--space-3);
  border-radius: var(--radius-md);
}

.item-add-btn:hover {
  border-color: var(--color-primary-300);
  color: var(--color-primary-600);
}

/* ── Tag Group ── */
.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-4);
}

/* ── Preview Card ── */
.preview-card {
  background: var(--bg-muted);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  margin-top: var(--space-4);
}

.preview-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--border-light);
}

.preview-row:last-child {
  border-bottom: none;
}

.preview-label {
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.preview-value {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-primary);
}

/* ── Step Actions ── */
.step-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--space-10);
  padding-top: var(--space-6);
  border-top: 1px solid var(--border-light);
}

/* ── Modal ── */
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
  width: 440px;
  max-width: 90vw;
  box-shadow: var(--shadow-xl);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--border-light);
}

.modal-header h3 {
  font-size: var(--text-lg);
  font-weight: 600;
}

.modal-close {
  padding: var(--space-1);
  font-size: var(--text-md);
  color: var(--text-muted);
}

.modal-body {
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.form-label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-secondary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--border-light);
}

@media (max-width: 640px) {
  .style-cards {
    grid-template-columns: 1fr;
  }
  .select-grid {
    grid-template-columns: 1fr;
  }
}
</style>
