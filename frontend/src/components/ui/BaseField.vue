<template>
  <label class="base-field" :class="{ 'base-field--icon': icon, 'base-field--error': error }">
    <span v-if="label">{{ label }}</span>
    <div class="base-field__control">
      <Icon v-if="icon" :icon="icon" width="18" />
      <component
        :is="tag"
        v-bind="$attrs"
        :value="model"
        @input="onInput"
        @change="onInput"
        class="base-field__input"
      />
    </div>
    <small v-if="hint" class="base-field__hint">{{ hint }}</small>
    <small v-if="error" class="base-field__error">{{ error }}</small>
  </label>
</template>

<script setup>
import { Icon } from "@iconify/vue";

const props = defineProps({
  label: String,
  hint: String,
  icon: String,
  error: String,
  tag: { type: String, default: "input" },
});

const model = defineModel({ type: [String, Number], default: "" });

const onInput = (event) => {
  if (event?.target) {
    model.value = event.target.value;
    return;
  }
  model.value = event ?? "";
};
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

.base-field__error {
  color: #b91c1c;
  font-size: 0.8rem;
}

.base-field--error .base-field__control {
  border-color: rgba(239, 68, 68, 0.5);
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.12);
}
</style>
