<template>
  <button
    v-bind="$attrs"
    :class="['base-button', `base-button--${variant}`, { 'base-button--block': block, 'is-loading': loading }]"
    :disabled="disabled || loading"
    v-motion
    :initial="{ opacity: 0, y: 10 }"
    :enter="{ opacity: 1, y: 0, transition: { duration: 0.3 } }"
  >
    <span class="base-button__icon" v-if="icon">
      <Icon :icon="icon" width="18" />
    </span>
    <slot />
  </button>
</template>

<script setup>
import { Icon } from "@iconify/vue";

defineOptions({ inheritAttrs: false });

const props = defineProps({
  variant: { type: String, default: "primary" },
  icon: String,
  block: Boolean,
  loading: Boolean,
  disabled: Boolean,
});
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;

.base-button {
  border: none;
  border-radius: 999px;
  padding: 0.65rem 1.6rem;
  font-weight: 600;
  font-size: 0.95rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: transform $transition-base, box-shadow $transition-base;

  &--block {
    width: 100%;
  }

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: $shadow-hover;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &--primary {
    background: linear-gradient(135deg, $color-primary, #7c9bff);
    color: #fff;
  }

  &--secondary {
    background: rgba(31, 117, 255, 0.12);
    color: $color-primary;
  }

  &--ghost {
    background: #fff;
    border: 1px solid rgba(15, 23, 42, 0.1);
    color: $color-muted;
  }
}
</style>
