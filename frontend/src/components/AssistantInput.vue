<template>
  <div class="assistant-box" v-motion :initial="{ opacity: 0, y: 15 }" :enter="{ opacity: 1, y: 0 }">
    <div class="assistant-box__label">
      <Icon icon="solar:sparkle-linear" width="24" />
      <div>
        <p>AI-подбор по описанию</p>
        <small>Расскажите, какой объект ищете, и мы настроим фильтры</small>
      </div>
    </div>
    <textarea
      v-model="localQuery"
      rows="3"
      placeholder="Например: хочу двушку до 10 млн в Приморском районе рядом с метро"
    ></textarea>
    <div class="assistant-box__actions">
      <div class="hint">
        <Icon icon="solar:info-circle-outline" />
        <span>AI понимает бюджет, район, комнаты, тип жилья, требуемую площадь</span>
      </div>
      <BaseButton :loading="loading" icon="solar:magic-stick-3-line-duotone" @click="emit('parse', localQuery)">
        {{ loading ? 'Анализируем...' : 'Подобрать' }}
      </BaseButton>
    </div>
  </div>
</template>

<script setup>
import { Icon } from "@iconify/vue";
import { computed } from "vue";
import BaseButton from "@/components/ui/BaseButton.vue";

const props = defineProps({
  modelValue: { type: String, default: "" },
  loading: Boolean,
});
const emit = defineEmits(["update:modelValue", "parse"]);

const localQuery = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;
@use "@/styles/mixins" as *;

.assistant-box {
  @include card;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: radial-gradient(circle at top right, rgba(31, 117, 255, 0.08), transparent 60%), #fff;
}

.assistant-box__label {
  display: flex;
  gap: 0.8rem;
  align-items: center;

  small {
    color: $color-muted;
  }
}

textarea {
  border: none;
  resize: none;
  border-radius: $radius-lg;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.03);
}

.assistant-box__actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;

  .hint {
    display: flex;
    gap: 0.5rem;
    color: $color-muted;
  }

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
