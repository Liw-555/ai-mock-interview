import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import InterviewConfig from '../views/InterviewConfig.vue'
import InterviewChat from '../views/InterviewChat.vue'
import EvaluationReport from '../views/EvaluationReport.vue'
import HistoryPage from '../views/HistoryPage.vue'

const routes = [
  { path: '/', name: 'Home', component: HomePage },
  { path: '/config', name: 'Config', component: InterviewConfig },
  { path: '/interview/:sessionId', name: 'Interview', component: InterviewChat, props: true },
  { path: '/report/:sessionId', name: 'Report', component: EvaluationReport, props: true },
  { path: '/history', name: 'History', component: HistoryPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
