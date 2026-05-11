<template>
  <header class="app-header">
    <div class="header-inner">
      <router-link to="/" class="brand">
        <span class="brand-icon">◆</span>
        <span class="brand-text">InterviewAgent</span>
      </router-link>
      <nav class="nav-links">
        <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 6l6-4 6 4v7a1 1 0 01-1 1H3a1 1 0 01-1-1V6z"/></svg>
          首页
        </router-link>
        <router-link to="/history" class="nav-link" :class="{ active: $route.path === '/history' }">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="6"/><path d="M8 5v3l2 2"/></svg>
          历史记录
        </router-link>
      </nav>
    </div>
  </header>
</template>

<script setup>
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-light);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 var(--space-6);
  height: 56px;
}

.brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  text-decoration: none;
  color: var(--text-primary);
}

.brand-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-700));
  color: white;
  border-radius: var(--radius-sm);
  font-size: 12px;
}

.brand-text {
  font-size: var(--text-md);
  font-weight: 700;
  letter-spacing: -0.02em;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-muted);
  border-radius: var(--radius-md);
  text-decoration: none;
  transition: all var(--transition-fast);
}

.nav-link:hover {
  color: var(--text-primary);
  background: var(--color-gray-100);
}

.nav-link.active {
  color: var(--color-primary-700);
  background: var(--color-primary-50);
}
</style>
