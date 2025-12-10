<template>
  <div class="skeleton-block" :style="{ height }"></div>
</template>

<script setup>
const props = defineProps({
  height: { type: String, default: '120px' },
});
</script>

<style scoped lang="scss">
.skeleton-block {
  width: 100%;
  border-radius: 16px;
  background: linear-gradient(90deg, #e5e7eb 25%, #f9fafb 37%, #e5e7eb 63%);
  background-size: 400% 100%;
  animation: shimmer 1.4s ease infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
