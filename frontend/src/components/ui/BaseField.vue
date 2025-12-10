<template>
  <label class="base-field" :class="{ 'base-field--icon': icon }">
    <span v-if="label">{{ label }}</span>
    <div class="base-field__control">
      <Icon v-if="icon" :icon="icon" width="18" />
      <component
        :is="tag"
        v-bind="$attrs"
        v-model="model"
        class="base-field__input"
      />
    </div>
    <small v-if="hint" class="base-field__hint">{{ hint }}</small>
  </label>
</template>

<script setup>
import { Icon } from "@iconify/vue";

const props = defineProps({
  label: String,
  hint: String,
  icon: String,
  tag: { type: String, default: "input" },
});

const model = defineModel({ type: [String, Number], default: "" });
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;

.base-field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.9rem;

  span {
    font-weight: 600;
    color: $color-muted;
  }
}

.base-field__control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: $radius-md;
  background: #fff;
  border: 1px solid transparent;
  box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.08);
  transition: border $transition-base, box-shadow $transition-base;

  &:focus-within {
    border-color: $color-primary;
    box-shadow: 0 0 0 3px rgba(31, 117, 255, 0.15);
  }
}

.base-field__input {
  width: 100%;
  border: none;
  background: transparent;
  font-size: 1rem;
}

.base-field__hint {
  color: $color-muted;
  font-size: 0.8rem;
}
</style>
