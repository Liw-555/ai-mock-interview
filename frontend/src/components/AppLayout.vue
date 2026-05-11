<template>
  <div class="page-layout" :class="{ 'no-header': hideHeader }">
    <AppHeader v-if="!hideHeader" />
    <main class="page-content">
      <slot />
    </main>
  </div>
</template>

<script setup>
import AppHeader from './AppHeader.vue'

defineProps({
  hideHeader: {
    type: Boolean,
    default: false,
  },
})
</script>

<style scoped>
.page-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-body);
}

.page-layout.no-header {
  background: var(--bg-surface);
}

.page-content {
  flex: 1;
  width: 100%;
}
</style>
