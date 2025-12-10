<template>
  <span :class="['base-chip', `base-chip--${variant}`]">
    <Icon v-if="icon" :icon="icon" width="16" />
    <slot />
  </span>
</template>

<script setup>
import { Icon } from "@iconify/vue";

defineProps({
  variant: { type: String, default: 'neutral' },
  icon: String,
});
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;

.base-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;

  &--neutral {
    background: rgba(15, 23, 42, 0.05);
    color: $color-muted;
  }
  &--success {
    background: rgba(16, 185, 129, 0.15);
    color: $color-success;
  }
  &--warning {
    background: rgba(249, 115, 22, 0.15);
    color: $color-warning;
  }
}
</style>
