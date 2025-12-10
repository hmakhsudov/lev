<template>
  <div class="metric-pill">
    <Icon :icon="icon" width="20" />
    <div>
      <p class="metric-pill__label">{{ label }}</p>
      <p class="metric-pill__value">{{ value }}</p>
    </div>
  </div>
</template>

<script setup>
import { Icon } from "@iconify/vue";

defineProps({
  icon: { type: String, required: true },
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
});
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;

.metric-pill {
  display: flex;
  gap: 0.6rem;
  padding: 0.8rem;
  border-radius: $radius-md;
  background: rgba(31, 117, 255, 0.06);
  color: #0f172a;
}

.metric-pill__label {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: $color-muted;
  letter-spacing: 0.08em;
}

.metric-pill__value {
  font-weight: 700;
}
</style>
