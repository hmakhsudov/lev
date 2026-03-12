<template>
  <div class="assistant-page container">
    <div class="assistant-layout">
      <section class="assistant-panel">
        <div class="assistant-panel__header">
          <BaseChip icon="solar:sparkles-linear">AI ассистент</BaseChip>
          <h1>Диалог с Lev AI</h1>
          <p>AI распознаёт фильтры и сразу ищет подходящие квартиры.</p>
        </div>
        <AssistantInput v-model="query" :loading="loading" @parse="parse" />
        <transition name="fade">
          <div v-if="result" class="assistant-panel__result">
            <div class="summary-card">
              <Icon icon="solar:chat-line-bold" />
              <div>
                <p class="summary-card__label">Вывод AI</p>
                <p class="summary-card__text">{{ result.summary }}</p>
              </div>
            </div>
            <h3>Распознанные фильтры</h3>
            <div class="result-grid">
              <div
                v-for="(value, key) in result.filters"
                :key="key"
                class="result-chip"
              >
                <span>{{ labels[key] || key }}</span>
                <strong>{{ displayValue(value, key) }}</strong>
              </div>
            </div>
          </div>
        </transition>
      </section>
      <section class="assistant-history">
        <h2>Советы AI</h2>
        <ul>
          <li v-for="tip in tips" :key="tip.title">
            <Icon :icon="tip.icon" width="24" />
            <div>
              <strong>{{ tip.title }}</strong>
              <p>{{ tip.body }}</p>
            </div>
          </li>
        </ul>
      </section>
    </div>

    <section v-if="result" class="assistant-results">
      <div class="assistant-results__header">
        <div>
          <h2>Подходящие объекты ({{ result.count }})</h2>
          <p class="text-muted">Фильтры применены автоматически</p>
        </div>
      </div>
      <div v-if="result.results?.length" class="assistant-results__list">
        <ListingCard
          v-for="item in result.results"
          :key="item.id"
          :property="item"
        />
      </div>
      <div v-else class="assistant-results__empty">
        <img src="https://illustrations.popsy.co/gray/market-analysis.svg" alt="Нет вариантов" />
        <h3>Пока без совпадений</h3>
        <p>Попробуйте изменить запрос или расширить критерии.</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { Icon } from "@iconify/vue";
import { ref } from "vue";
import AssistantInput from "@/components/AssistantInput.vue";
import ListingCard from "@/components/ListingCard.vue";
import BaseChip from "@/components/ui/BaseChip.vue";
import api from "@/services/api";

const query = ref("");
const loading = ref(false);
const result = ref(null);
const labels = { rooms: "Комнаты", price_max: "Макс. цена", district: "Район", city: "Город", property_type: "Тип" };

const tips = [
  { title: "Укажите станции метро", body: "Например: рядом с метро Чкаловская", icon: "solar:metro-line-duotone" },
  { title: "Добавьте площадь", body: "AI умеет понимать диапазоны и сравнения", icon: "solar:ruler-cross-broken" },
  { title: "Сравните районы", body: "Можно просить несколько районов сразу", icon: "solar:map-point-line-duotone" },
];

const parse = async () => {
  loading.value = true;
  try {
    const { data } = await api.post("/assistant/parse-query/", { query: query.value });
    result.value = data;
  } catch (error) {
    result.value = {
      summary: "Не удалось обработать запрос",
      filters: {},
      results: [],
      count: 0,
    };
  } finally {
    loading.value = false;
  }
};

const displayValue = (value, key) => {
  if (value == null) return "—";
  if (key === "price_max") {
    return new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(
      value,
    );
  }
  return value;
};
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;
@use "@/styles/mixins" as *;

.assistant-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(0, 0.7fr);
  gap: 2rem;

  @include mobile {
    grid-template-columns: 1fr;
  }
}

.assistant-panel {
  @include card;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;

  @include mobile {
    padding: 1.5rem;
  }
}

.assistant-panel__header h1 {
  @include heading-xl;
  margin-top: 0.5rem;
}

.assistant-panel__result {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: rgba(31, 117, 255, 0.04);
  border-radius: $radius-lg;
  padding: 1.5rem;
}

.summary-card {
  display: flex;
  gap: 0.8rem;
  align-items: flex-start;
  padding: 1rem;
  border-radius: $radius-md;
  background: #fff;
  box-shadow: $shadow-soft;

  &__label {
    color: $color-muted;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
  }

  &__text {
    font-weight: 600;
  }
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;

  @include mobile {
    grid-template-columns: 1fr;
  }
}

.result-chip {
  background: #fff;
  border-radius: $radius-md;
  padding: 0.9rem;
  box-shadow: $shadow-soft;
  span {
    color: $color-muted;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
  }
}

.assistant-history {
  @include card;
  padding: 2rem;
}

.assistant-history ul {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.assistant-history li {
  display: flex;
  gap: 0.8rem;
  padding: 1rem;
  border-radius: $radius-md;
  background: rgba(15, 23, 42, 0.03);
}

.assistant-results {
  margin-top: 2rem;
  @include card;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.assistant-results__list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.assistant-results__empty {
  text-align: center;
  img {
    width: 200px;
    margin-inline: auto;
  }
  p {
    color: $color-muted;
  }
}
</style>
