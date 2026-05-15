<template>
  <div class="home container">
    <section class="hero">
      <div class="hero__content" v-motion :initial="{ opacity: 0, y: 25 }" :enter="{ opacity: 1, y: 0 }">
        <h1>Подбор недвижимости с использованием ИИ</h1>
        <p>
          Опишите квартиру мечты, укажите бюджет, район или станцию метро — Lev Estate преобразует запрос в фильтры,
          загрузит объявления и покажет всё на карте с живой аналитикой.
        </p>
        <div class="hero__stats">
          <div>
            <strong>5 200+</strong>
            <span>актуальных объектов</span>
          </div>
          <!-- <div>
            <strong>Быстрый</strong>
            <span>подбор</span>
          </div> -->
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

    <div class="filters-inline">
      <FilterForm v-model="filters" @submit="submitFilters" @reset="resetFilters" />
    </div>

    <div class="mobile-controls">
      <button class="mobile-controls__btn" type="button" @click="openFilters">Фильтры</button>
      <div class="mobile-controls__toggle">
        <button :class="{ active: mobileView === 'list' }" @click="setMobileView('list')">Список</button>
        <button :class="{ active: mobileView === 'map' }" @click="setMobileView('map')">Карта</button>
      </div>
    </div>

    <div v-if="filtersOpen" class="filters-sheet">
      <div class="filters-sheet__backdrop" @click="closeFilters" />
      <div class="filters-sheet__panel">
        <div class="filters-sheet__header">
          <h3>Фильтры</h3>
          <button type="button" class="filters-sheet__close" @click="closeFilters">Закрыть</button>
        </div>
        <FilterForm v-model="filters" @submit="applyFilters" @reset="resetFilters" />
      </div>
    </div>

    <section
      class="content"
      :class="{
        'content--full': viewMode === 'grid',
        'content--mobile-map': mobileView === 'map',
        'content--mobile-list': mobileView === 'list',
      }"
    >
      <div class="content__list">
        <div class="content__list-header">
          <div>
            <h2>Найдено {{ totalCount }} объектов</h2>
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
                :layout="viewMode === 'grid' ? 'grid' : 'list'"
                @focus-map="focusOnProperty"
              />
            </transition-group>
            <div v-if="!properties.length" class="empty-state">
              <img src="https://illustrations.popsy.co/gray/workflow-ui.svg" alt="Нет объектов" />
              <h3>Пусто, но не надолго</h3>
              <p>Попробуйте изменить фильтры или сбросить их.</p>
            </div>
            <nav v-if="totalPages > 1" class="pagination" aria-label="Пагинация объектов">
              <button type="button" :disabled="page === 1" @click="goToPage(page - 1)">Назад</button>
              <span>Страница {{ page }} из {{ totalPages }}</span>
              <button type="button" :disabled="page === totalPages" @click="goToPage(page + 1)">Вперёд</button>
            </nav>
          </template>
        </div>
      </div>
      <div v-if="viewMode === 'list'" class="content__map" ref="mapWrapper">
        <RealEstateMap
          :listings="properties"
          :selected-id="selectedProperty?.id"
          @marker-click="handleMarkerClick"
        />
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
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import AssistantInput from "@/components/AssistantInput.vue";
import FilterForm from "@/components/FilterForm.vue";
import ListingCard from "@/components/ListingCard.vue";
import RealEstateMap from "@/components/RealEstateMap.vue";
import SkeletonBlock from "@/components/ui/SkeletonBlock.vue";
import api from "@/services/api";

const properties = ref([]);
const aiQuery = ref("");
const assistantLoading = ref(false);
const router = useRouter();
const loading = ref(true);
const viewMode = ref("list");
const selectedProperty = ref(null);
const mapWrapper = ref(null);
const filtersOpen = ref(false);
const mobileView = ref("list");
const page = ref(1);
const pageSize = 12;
const totalCount = ref(0);

const filters = ref({});
const lastUpdated = computed(() => new Date().toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" }));
const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize)));

const normalizeListResponse = (data) => {
  if (Array.isArray(data)) {
    return { results: data, count: data.length };
  }
  return {
    results: data?.results || [],
    count: Number(data?.count || 0),
  };
};

const cleanParams = () => {
  const params = { ...filters.value, page: page.value, page_size: pageSize };
  Object.keys(params).forEach((key) => {
    if (params[key] === "" || params[key] === null || params[key] === undefined) {
      delete params[key];
    }
  });
  return params;
};

const fetchProperties = async () => {
  loading.value = true;
  try {
    const { data } = await api.get("/properties/", { params: cleanParams() });
    const normalized = normalizeListResponse(data);
    properties.value = normalized.results;
    totalCount.value = normalized.count;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const handleAssistant = (text) => {
  const query = String(text || "").trim();
  if (!query) return;
  router.push({ path: "/assistant", query: { q: query } });
};

const resetFilters = () => {
  filters.value = {};
  page.value = 1;
  fetchProperties();
};

const submitFilters = () => {
  page.value = 1;
  fetchProperties();
};

const goToPage = (nextPage) => {
  page.value = Math.min(Math.max(nextPage, 1), totalPages.value);
  fetchProperties();
};

const focusOnProperty = (property) => {
  selectedProperty.value = property;
  if (mapWrapper.value) {
    mapWrapper.value.scrollIntoView({ behavior: "smooth", block: "start" });
  }
};

const handleMarkerClick = (property) => {
  selectedProperty.value = property;
};

const openFilters = () => {
  filtersOpen.value = true;
};

const closeFilters = () => {
  filtersOpen.value = false;
};

const applyFilters = async () => {
  page.value = 1;
  await fetchProperties();
  closeFilters();
};

const setMobileView = (value) => {
  mobileView.value = value;
  viewMode.value = "list";
};

watch(filtersOpen, (value) => {
  document.body.style.overflow = value ? "hidden" : "";
});

const handleListingCreated = () => {
  fetchProperties();
};

onMounted(() => {
  fetchProperties();
  window.addEventListener("listing:created", handleListingCreated);
});

onBeforeUnmount(() => {
  window.removeEventListener("listing:created", handleListingCreated);
});
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
  align-items: start;

  @include mobile {
    grid-template-columns: 1fr;
  }
}

.hero__content h1 {
  @include heading-xl;
  margin: 0 0 1rem;
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

  @include mobile {
    grid-template-columns: 1fr;
  }
}

.hero__assistant {
  align-self: end;
  margin-top: 4.5rem;

  @include mobile {
    margin-top: 0;
    align-self: stretch;
  }
}

.content {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr);
  gap: 1.5rem;

  @include mobile {
    grid-template-columns: 1fr;
  }
}

.content--full {
  grid-template-columns: 1fr;
}

.filters-inline {
  @include mobile {
    display: none;
  }
}

.mobile-controls {
  display: none;
  flex-direction: column;
  gap: 0.75rem;

  @include mobile {
    display: flex;
  }

  &__btn {
    border: none;
    background: $color-primary;
    color: #fff;
    border-radius: 999px;
    padding: 0.75rem 1.2rem;
    font-weight: 600;
  }

  &__toggle {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
    background: #fff;
    border-radius: 999px;
    padding: 0.25rem;

    button {
      border: none;
      background: transparent;
      padding: 0.6rem;
      border-radius: 999px;
      font-weight: 600;

      &.active {
        background: rgba(31, 117, 255, 0.1);
        color: $color-primary;
      }
    }
  }
}

.filters-sheet {
  position: fixed;
  inset: 0;
  z-index: 90;
  display: flex;
  align-items: flex-end;

  &__backdrop {
    position: absolute;
    inset: 0;
    background: rgba(15, 23, 42, 0.4);
  }

  &__panel {
    position: relative;
    width: 100%;
    max-height: 85vh;
    overflow-y: auto;
    background: #fff;
    border-radius: 20px 20px 0 0;
    padding: 1rem 1rem 2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
  }

  &__close {
    border: none;
    background: rgba(15, 23, 42, 0.06);
    border-radius: 999px;
    padding: 0.5rem 1rem;
    font-weight: 600;
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

  @include mobile {
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

  @include mobile {
    display: none;
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
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.25rem;
  align-items: stretch;

  @include mobile {
    grid-template-columns: 1fr;
  }
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

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  padding: 0.5rem 0 1rem;

  button {
    border: none;
    border-radius: 999px;
    padding: 0.65rem 1.2rem;
    background: $color-primary;
    color: #fff;
    font-weight: 700;
    cursor: pointer;

    &:disabled {
      background: rgba(15, 23, 42, 0.12);
      color: $color-muted;
      cursor: not-allowed;
    }
  }

  span {
    color: $color-muted;
    font-weight: 600;
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

  @include mobile {
    position: static;
    height: 60vh;
  }
}

.map-legend {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  color: $color-muted;
  font-size: 0.85rem;
}

@include mobile {
  .content--mobile-map .content__list {
    display: none;
  }

  .content--mobile-list .content__map {
    display: none;
  }
}
</style>
