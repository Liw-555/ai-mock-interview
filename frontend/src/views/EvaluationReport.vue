<template>
  <AppLayout>
    <div class="report-container">
      <!-- Page Header -->
      <div class="page-header">
        <router-link to="/history" class="back-link">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10 3L5 8l5 5"/></svg>
          返回历史
        </router-link>
        <h1 class="page-title">面试评估报告</h1>
      </div>

      <!-- Loading / Error -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在加载报告...</p>
      </div>
      <div v-else-if="error" class="error-state">
        <svg width="24" height="24" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="6"/><path d="M8 5v3M8 10h.01"/></svg>
        <p>{{ error }}</p>
      </div>

      <!-- Report Content -->
      <template v-if="report && !error">
        <!-- Summary Card -->
        <div class="summary-card animate-fade-in">
          <div class="summary-header">
            <h2 class="summary-title">{{ reportTitle }}</h2>
            <span :class="['score-badge', scoreLevel]">{{ report.total_score ?? 0 }} 分</span>
          </div>

          <div class="score-section">
            <div class="total-score">
              <div class="score-circle" :class="scoreLevel">
                <span class="score-num">{{ report.total_score ?? 0 }}</span>
              </div>
              <span class="score-out-of">/ 100</span>
            </div>

            <div class="dimensions">
              <div v-for="(label, key) in dimensionLabels" :key="key" class="dim-row">
                <span class="dim-label">{{ label }}</span>
                <div class="dim-bar">
                  <div class="dim-bar-fill" :style="{ width: ((report[key] || 0) / 5 * 100) + '%' }"></div>
                </div>
                <div class="dim-stars">
                  <span v-for="i in 5" :key="i" :class="i <= (report[key] || 0) ? 'star-filled' : 'star-empty'">★</span>
                </div>
                <span class="dim-score">{{ report[key] || 0 }}</span>
              </div>
            </div>
          </div>

          <div class="radar-chart" ref="radarChart"></div>
        </div>

        <!-- Per-Question Review -->
        <div class="section-card" v-if="report?.per_question?.length">
          <h3 class="section-title">
            <svg width="18" height="18" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 2h12v12H2z"/><path d="M5 6h6M5 9h4"/></svg>
            逐题点评
          </h3>
          <div class="question-list">
            <div v-for="(q, idx) in report.per_question" :key="idx" class="question-card">
              <div class="question-header">
                <span class="question-num">Q{{ idx + 1 }}</span>
                <span class="question-summary">{{ q.question_summary }}</span>
              </div>
              <div class="question-body">
                <div class="question-quote">
                  <label>你的回答</label>
                  <p>{{ q.user_quote }}</p>
                </div>
                <div class="question-scores" v-if="q.scores">
                  <span v-for="(val, dim) in q.scores" :key="dim" class="mini-badge">
                    {{ dimensionLabels[dim] || dim }} {{ val }}
                  </span>
                </div>
                <div class="question-comment">
                  <label>评语</label>
                  <p>{{ q.comment }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Improvement Suggestions -->
        <div class="section-card" v-if="report?.improvement_suggestions?.length">
          <h3 class="section-title">
            <svg width="18" height="18" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 1l2 5h5l-4 3 1.5 5L8 11 3.5 14 5 9 1 6h5z"/></svg>
            改进建议
          </h3>
          <div class="suggestion-list">
            <div v-for="(s, idx) in report.improvement_suggestions" :key="idx" :class="['suggestion-card', `priority-${s.priority}`]">
              <div class="suggestion-header">
                <span :class="['priority-dot', `p-${s.priority}`]"></span>
                <strong>{{ s.dimension }}</strong>
                <span class="suggestion-score">{{ s.score }} 分</span>
              </div>
              <p class="suggestion-text">{{ s.suggestion }}</p>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="report-actions">
          <router-link to="/" class="btn btn-primary btn-lg">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 2v8m0-8L5 5m3-3l3 3M2 10v2a2 2 0 002 2h8a2 2 0 002-2v-2"/></svg>
            再来一次
          </router-link>
          <router-link to="/history" class="btn btn-secondary btn-lg">返回历史</router-link>
        </div>
      </template>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { useInterviewStore } from '../stores/interview.js'
import AppLayout from '../components/AppLayout.vue'

const route = useRoute()
const interviewStore = useInterviewStore()
const sessionId = route.params.sessionId

const report = ref(null)
const radarChart = ref(null)
const loading = ref(true)
const error = ref('')

const reportTitle = computed(() => {
  if (!report.value) return '面试评估报告'
  const company = report.value.target_company || '未知公司'
  const roundLabel = report.value.interview_round === 'hr' ? 'HR面' : '业务面'
  return `${company} · ${roundLabel}`
})

const scoreLevel = computed(() => {
  const s = report.value?.total_score ?? 0
  if (s >= 80) return 'excellent'
  if (s >= 60) return 'good'
  if (s >= 40) return 'average'
  return 'needs-work'
})

const dimensionLabels = {
  product_thinking: '产品思维',
  data_ability: '数据能力',
  project_depth: '项目深度',
  expression_logic: '表达逻辑',
  business_understanding: '业务理解',
}

onMounted(async () => {
  try {
    report.value = await interviewStore.getReport(sessionId)
    nextTick(() => renderRadar())
  } catch (err) {
    console.error('Failed to load report:', err)
    error.value = err.message || '加载报告失败，请稍后重试'
  } finally {
    loading.value = false
  }
})

function renderRadar() {
  if (!radarChart.value || !report.value) return
  const chart = echarts.init(radarChart.value)
  const dims = ['product_thinking', 'data_ability', 'project_depth', 'expression_logic', 'business_understanding']
  const labels = dims.map(d => dimensionLabels[d])
  const values = dims.map(d => report.value[d] || 0)

  chart.setOption({
    radar: {
      indicator: labels.map(l => ({ name: l, max: 5 })),
      shape: 'polygon',
      splitNumber: 5,
      axisName: {
        color: '#6b7280',
        fontSize: 12,
      },
      splitArea: {
        areaStyle: {
          color: ['#f9fafb', '#f3f4f6', '#f9fafb', '#f3f4f6', '#f9fafb'],
        },
      },
      splitLine: {
        lineStyle: {
          color: '#e5e7eb',
        },
      },
      axisLine: {
        lineStyle: {
          color: '#e5e7eb',
        },
      },
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        name: '评分',
        areaStyle: {
          color: 'rgba(99, 102, 241, 0.15)',
        },
        lineStyle: {
          color: '#6366f1',
          width: 2,
        },
        itemStyle: {
          color: '#6366f1',
        },
      }],
    }],
  })

  // Responsive resize
  window.addEventListener('resize', () => chart.resize())
}

function formatScores(scores) {
  if (!scores) return ''
  return Object.entries(scores).map(([k, v]) => `${dimensionLabels[k] || k} ${v}分`).join(' / ')
}
</script>

<style scoped>
.report-container {
  max-width: 800px;
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

/* ── Loading / Error ── */
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
  padding: var(--space-16) 0;
  color: var(--text-muted);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-gray-200);
  border-top-color: var(--color-primary-500);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.error-state {
  color: var(--color-error-500);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── Summary Card ── */
.summary-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-6);
}

.summary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-8);
}

.summary-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.score-badge {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: 700;
}
.score-badge.excellent { background: #ecfdf5; color: #059669; }
.score-badge.good { background: #eff6ff; color: #2563eb; }
.score-badge.average { background: #fffbeb; color: #d97706; }
.score-badge.needs-work { background: #fef2f2; color: #dc2626; }

/* ── Score Section ── */
.score-section {
  display: flex;
  gap: var(--space-10);
  align-items: flex-start;
  margin-bottom: var(--space-8);
}

.total-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
}

.score-circle {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 4px solid;
}
.score-circle.excellent { border-color: #10b981; }
.score-circle.good { border-color: #3b82f6; }
.score-circle.average { border-color: #f59e0b; }
.score-circle.needs-work { border-color: #ef4444; }

.score-num {
  font-size: var(--text-3xl);
  font-weight: 800;
  color: var(--text-primary);
}

.score-out-of {
  font-size: var(--text-sm);
  color: var(--text-muted);
}

/* ── Dimensions ── */
.dimensions {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.dim-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.dim-label {
  width: 64px;
  font-size: var(--text-sm);
  color: var(--text-secondary);
  flex-shrink: 0;
}

.dim-bar {
  flex: 1;
  height: 6px;
  background: var(--color-gray-100);
  border-radius: 3px;
  overflow: hidden;
}

.dim-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary-400), var(--color-primary-600));
  border-radius: 3px;
  transition: width var(--transition-slow);
}

.dim-stars {
  display: flex;
  gap: 1px;
  font-size: var(--text-xs);
}

.star-filled {
  color: #f59e0b;
}

.star-empty {
  color: var(--color-gray-300);
}

.dim-score {
  width: 24px;
  text-align: right;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
}

/* ── Radar Chart ── */
.radar-chart {
  width: 100%;
  height: 320px;
  margin-top: var(--space-4);
}

/* ── Section Card ── */
.section-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-xs);
  margin-bottom: var(--space-6);
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-5);
}

/* ── Question List ── */
.question-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.question-card {
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.question-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--bg-muted);
}

.question-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: var(--color-primary-600);
  color: white;
  border-radius: 50%;
  font-size: var(--text-xs);
  font-weight: 700;
  flex-shrink: 0;
}

.question-summary {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.question-body {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.question-body label {
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.question-quote p,
.question-comment p {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
  margin-top: var(--space-1);
}

.question-scores {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.mini-badge {
  padding: 2px var(--space-2);
  background: var(--color-primary-50);
  color: var(--color-primary-700);
  border-radius: var(--radius-sm);
  font-size: 11px;
  font-weight: 500;
}

/* ── Suggestion List ── */
.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.suggestion-card {
  border: 1px solid var(--border-light);
  border-left: 4px solid;
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.suggestion-card.priority-高 { border-left-color: var(--color-error-500); }
.suggestion-card.priority-中 { border-left-color: var(--color-warning-500); }
.suggestion-card.priority-低 { border-left-color: var(--color-success-500); }

.suggestion-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}

.priority-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.priority-dot.p-高 { background: var(--color-error-500); }
.priority-dot.p-中 { background: var(--color-warning-500); }
.priority-dot.p-低 { background: var(--color-success-500); }

.suggestion-score {
  margin-left: auto;
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.suggestion-text {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
}

/* ── Actions ── */
.report-actions {
  display: flex;
  justify-content: center;
  gap: var(--space-4);
  margin-top: var(--space-8);
}

@media (max-width: 640px) {
  .score-section {
    flex-direction: column;
    align-items: center;
  }
}
</style>
