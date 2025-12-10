<template>
  <div class="home container">
    <section class="hero">
      <div class="hero__content" v-motion :initial="{ opacity: 0, y: 25 }" :enter="{ opacity: 1, y: 0 }">
        <BaseChip icon="solar:stars-bold" variant="neutral">Lev AI</BaseChip>
        <h1>Подбор недвижимости с интеллектом уровня премиальных агентств</h1>
        <p>
          Опишите квартиру мечты, укажите бюджет, район или станцию метро — Lev Estate преобразует запрос в фильтры,
          загрузит объявления и покажет всё на карте с живой аналитикой.
        </p>
        <div class="hero__stats">
          <div>
            <strong>5 200+</strong>
            <span>актуальных объектов</span>
          </div>
          <div>
            <strong>12 сек</strong>
            <span>до готового подбора</span>
          </div>
          <div>
            <strong>24/7</strong>
            <span>AI ассистент</span>
          </div>
        </div>
      </div>
      <div class="hero__assistant">
        <AssistantInput v-model="aiQuery" :loading="assistantLoading" @parse="handleAssistant" />
      </div>
    </section>

    <FilterForm v-model="filters" @submit="fetchProperties" @reset="resetFilters" />

    <section class="content">
      <div class="content__list">
        <div class="content__list-header">
          <div>
            <h2>Найдено {{ properties.length }} объектов</h2>
            <p class="text-muted">Обновлено {{ lastUpdated }}</p>
          </div>
          <div class="view-switch">
            <button :class="{ active: viewMode === 'list' }" @click="viewMode = 'list'">
              <Icon icon="solar:rows-linear" /> Списком
            </button>
            <button :class="{ active: viewMode === 'grid' }" @click="viewMode = 'grid'">
              <Icon icon="solar:widget-5-linear" /> Сеткой
            </button>
          </div>
        </div>
        <div class="cards" :class="`cards--${viewMode}`">
          <template v-if="loading">
            <SkeletonBlock v-for="n in 3" :key="`skeleton-${n}`" height="280px" />
          </template>
          <template v-else>
            <transition-group name="fade" tag="div" class="cards__inner">
              <ListingCard
                v-for="item in properties"
                :key="item.id"
                :property="item"
                @focus-map="focusOnProperty"
              />
            </transition-group>
            <div v-if="!properties.length" class="empty-state">
              <img src="https://illustrations.popsy.co/gray/workflow-ui.svg" alt="Нет объектов" />
              <h3>Пусто, но не надолго</h3>
              <p>Попробуйте изменить фильтры или уточнить запрос для ассистента.</p>
              <BaseButton icon="solar:magic-star-line-duotone" @click="handleAssistant(aiQuery)">
                Спросить AI снова
              </BaseButton>
            </div>
          </template>
        </div>
      </div>
      <div class="content__map" ref="mapWrapper">
        <ListingsMap :properties="properties" :selected-property-id="selectedProperty?.id" />
        <div class="map-legend">
          <p><Icon icon="solar:pin-linear" /> Каждая точка — квартира с ценой в маркере.</p>
          <p><Icon icon="solar:mouse-circle-linear" /> Наведите, чтобы увидеть адрес.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { Icon } from "@iconify/vue";
import { computed, onMounted, ref } from "vue";
import AssistantInput from "@/components/AssistantInput.vue";
import FilterForm from "@/components/FilterForm.vue";
import ListingCard from "@/components/ListingCard.vue";
import ListingsMap from "@/components/ListingsMap.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseChip from "@/components/ui/BaseChip.vue";
import SkeletonBlock from "@/components/ui/SkeletonBlock.vue";
import api from "@/services/api";

const properties = ref([]);
const aiQuery = ref("");
const assistantLoading = ref(false);
const loading = ref(true);
const viewMode = ref("list");
const selectedProperty = ref(null);
const mapWrapper = ref(null);

const filters = ref({ city: "Санкт-Петербург" });
const lastUpdated = computed(() => new Date().toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" }));

const fetchProperties = async () => {
  loading.value = true;
  try {
    const { data } = await api.get("/properties/", { params: filters.value });
    properties.value = data;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const handleAssistant = async (text) => {
  assistantLoading.value = true;
  try {
    const { data } = await api.post("/assistant/parse-query/", { query: text });
    filters.value = { ...filters.value, ...data.filters };
    await fetchProperties();
  } catch (error) {
    console.error(error);
  } finally {
    assistantLoading.value = false;
  }
};

const resetFilters = () => {
  filters.value = { city: "Санкт-Петербург" };
  fetchProperties();
};

const focusOnProperty = (property) => {
  selectedProperty.value = property;
  if (mapWrapper.value) {
    mapWrapper.value.scrollIntoView({ behavior: "smooth", block: "start" });
  }
};

onMounted(fetchProperties);
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;
@use "@/styles/mixins" as *;

.home {
  display: flex;
  flex-direction: column;
  gap: $spacing-2xl;
}

.hero {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  align-items: center;
}

.hero__content h1 {
  @include heading-xl;
  margin: 1rem 0;
}

.hero__stats {
  margin-top: 1.5rem;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;

  strong {
    font-size: 1.8rem;
  }

  span {
    color: $color-muted;
    font-size: 0.85rem;
  }
}

.hero__assistant {
  align-self: stretch;
}

.content {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr);
  gap: 1.5rem;

  @media (max-width: 1100px) {
    grid-template-columns: 1fr;
  }
}

.content__list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.content__list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
  }
}

.view-switch {
  display: inline-flex;
  gap: 0.5rem;
  background: rgba(15, 23, 42, 0.05);
  border-radius: 999px;
  padding: 0.25rem;

  button {
    border: none;
    background: transparent;
    padding: 0.45rem 0.9rem;
    border-radius: 999px;
    display: flex;
    align-items: center;
    gap: 0.3rem;
    color: $color-muted;

    &.active {
      background: #fff;
      box-shadow: $shadow-soft;
      color: $color-primary;
    }
  }
}

.cards {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.cards__inner {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.cards--grid .cards__inner {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.25rem;
}

.empty-state {
  @include card;
  text-align: center;
  padding: 2rem;
  img {
    width: 200px;
    margin-inline: auto;
  }
  h3 {
    margin: 1rem 0 0.5rem;
  }
  p {
    color: $color-muted;
    margin-bottom: 1.5rem;
  }
}

.content__map {
  position: sticky;
  top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  align-self: flex-start;
  height: calc(100vh - 2.5rem);

  :deep(.map) {
    height: 100%;
  }
}

.map-legend {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  color: $color-muted;
  font-size: 0.85rem;
}
</style>
