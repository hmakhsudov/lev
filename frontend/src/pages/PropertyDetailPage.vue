<template>
  <div class="detail-page container" v-if="property">
    <nav class="detail-breadcrumbs">
      <RouterLink to="/">Главная</RouterLink>
      <span>/</span>
      <span>Квартиры</span>
      <span>/</span>
      <span>{{ property.city || "Город уточняется" }}</span>
      <span v-if="property.district">/</span>
      <span v-if="property.district">{{ property.district }}</span>
    </nav>

    <header class="detail-header">
      <div>
        <BaseChip icon="solar:map-point-bold" variant="neutral">
          {{ property.district || "Район уточняется" }}
        </BaseChip>
        <h1>{{ headerTitle }}</h1>
        <p>
          <Icon icon="solar:map-point-line-duotone" />
          {{ property.address || locationLine }}
        </p>
        <ul class="detail-header__meta">
          <li>{{ propertyTypeLabel }}</li>
          <li>{{ roomsLabel }}</li>
          <li>{{ areaLabel }}</li>
          <li v-if="floorLabel">{{ floorLabel }}</li>
        </ul>
      </div>
      <div class="detail-header__actions">
        <button type="button" :class="{ active: isFavorited }" @click="toggleFavorite">
          <Icon :icon="isFavorited ? 'solar:heart-bold' : 'solar:heart-linear'" />
          {{ isFavorited ? "В избранном" : "В избранное" }}
        </button>
        <button type="button" @click="shareProperty"><Icon icon="solar:share-linear" /> Поделиться</button>
      </div>
    </header>

    <section class="detail-layout">
      <div class="detail-main">
        <section class="detail-gallery">
          <div class="photo-count" v-if="gallery.length > 1">
            <Icon icon="solar:camera-line-duotone" /> {{ gallery.length }} фото
          </div>
          <Swiper
            :modules="modules"
            :slides-per-view="1"
            :navigation="true"
            :pagination="{ clickable: true }"
            class="detail-gallery__slider"
            @swiper="onSwiper"
            @slideChange="onSlideChange"
          >
            <SwiperSlide v-for="(img, idx) in gallery" :key="idx">
              <img :src="img" :alt="property.title" @click="openLightbox(idx)" />
            </SwiperSlide>
          </Swiper>
          <div class="detail-gallery__thumbs" v-if="gallery.length > 1">
            <button
              v-for="(img, idx) in gallery"
              :key="`thumb-${idx}`"
              :class="['thumb', { active: idx === activeSlide }]"
              @click="goToSlide(idx)"
            >
              <img :src="img" :alt="`Фото ${idx + 1}`" />
            </button>
          </div>
        </section>

        <section class="detail-info">
          <div class="detail-info__mobile-price">
            <PriceBlock :property="property" :price-status="priceStatus" />
          </div>
          <section class="detail-description">
            <h2>Описание</h2>
            <p>{{ property.description || placeholder }}</p>
          </section>
          <section class="detail-features">
            <h2>Характеристики</h2>
            <div class="feature-grid">
              <div v-for="item in features" :key="item.label">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </section>
          <section class="detail-map">
            <div class="detail-map__header">
              <h2>Расположение</h2>
              <span>{{ property.address || locationLine }}</span>
            </div>
            <RealEstateMap :listings="[property]" :selected-id="property.id" />
          </section>
          <section class="detail-similar" v-if="similar.length">
            <div class="detail-similar__header">
              <h2>Похожие объекты</h2>
              <p>Мы подобрали ещё предложения поблизости</p>
            </div>
            <div class="detail-similar__list">
              <ListingCard v-for="item in similar" :key="item.id" :property="item" layout="grid" />
            </div>
          </section>
        </section>
      </div>

      <aside class="detail-sidebar">
        <PriceBlock :property="property" :price-status="priceStatus" />
        <div class="contact-card">
          <h3>Контакт</h3>
          <div v-if="agent" class="agent">
            <strong>{{ agentName }}</strong>
            <span>{{ agent.email }}</span>
            <span>{{ agentRole }}</span>
          </div>
          <p v-else class="text-muted">
            Объект загружен из внешнего источника. Диалог доступен только для объектов, созданных агентом на сайте.
          </p>
          <BaseButton
            v-if="agent"
            icon="solar:chat-round-line-duotone"
            variant="secondary"
            block
            @click="startChat"
          >
            Написать агенту
          </BaseButton>
        </div>
      </aside>
    </section>

    <transition name="fade">
      <div v-if="toastMessage" class="detail-toast">{{ toastMessage }}</div>
    </transition>

    <VueEasyLightbox
      :visible="lightboxVisible"
      :imgs="gallery"
      :index="lightboxIndex"
      @hide="lightboxVisible = false"
    />
  </div>
  <div v-else class="container loading-state">
    <SkeletonBlock height="420px" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, RouterLink, useRouter } from "vue-router";
import { Icon } from "@iconify/vue";
import { Swiper, SwiperSlide } from "swiper/vue";
import { Navigation, Pagination } from "swiper/modules";
import VueEasyLightbox from "vue-easy-lightbox";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseChip from "@/components/ui/BaseChip.vue";
import RealEstateMap from "@/components/RealEstateMap.vue";
import ListingCard from "@/components/ListingCard.vue";
import PriceBlock from "@/components/PriceBlock.vue";
import SkeletonBlock from "@/components/ui/SkeletonBlock.vue";
import { formatArea, formatFloor, formatRooms, safeNumber } from "@/utils/formatters";
import api from "@/services/api";
import { useAuthStore } from "@/store/auth";
import { useFavoritesStore } from "@/store/favorites";
import { useChatStore } from "@/store/chat";

const route = useRoute();
const router = useRouter();
const property = ref(null);
const similar = ref([]);
const modules = [Navigation, Pagination];
const placeholder = "Апартамент расположен в районе с развитой инфраструктурой и хорошей транспортной доступностью.";
const swiperRef = ref(null);
const activeSlide = ref(0);
const lightboxVisible = ref(false);
const lightboxIndex = ref(0);
const fallbackImage =
  "https://images.unsplash.com/photo-1505693314120-0d443867891c?w=1200&auto=format&fit=crop";
const auth = useAuthStore();
const favorites = useFavoritesStore();
const chat = useChatStore();
const toastMessage = ref("");
let toastTimer = null;

const showToast = (message) => {
  toastMessage.value = message;
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => {
    toastMessage.value = "";
  }, 2400);
};

const gallery = computed(() => {
  if (!property.value) return [fallbackImage];
  const main = property.value.main_image;
  const list = property.value.images?.length ? property.value.images : [];
  const unique = [...new Set([main, ...list].filter(Boolean))];
  return unique.length ? unique : [fallbackImage];
});

const headerTitle = computed(() => {
  if (!property.value) return "";
  return property.value.title || `${formatRooms(property.value.rooms)} ${formatArea(property.value.area_total)}`;
});

const locationLine = computed(() => {
  if (!property.value) return "";
  const city = property.value.city || "Город";
  const district = property.value.district ? `${property.value.district}` : "";
  return district ? `${city}, ${district}` : city;
});

const priceStatus = computed(() => {
  const predicted = safeNumber(property.value?.predicted_price);
  const price = safeNumber(property.value?.price);
  if (!predicted || !price) return { label: "", hint: "", class: "" };
  if (predicted > price) return { label: "Выгодное предложение", hint: "Цена ниже прогноза", class: "is-good" };
  if (predicted < price) return { label: "Цена выше рынка", hint: "Есть простор для торга", class: "is-risk" };
  return { label: "Рыночная цена", hint: "Соответствует прогнозу", class: "" };
});

const agent = computed(() => property.value?.agent || null);
const agentName = computed(() => {
  if (!agent.value) return "";
  const full = [agent.value.first_name, agent.value.last_name].filter(Boolean).join(" ");
  return full || "Агент";
});
const agentRole = computed(() => {
  if (!agent.value) return "";
  return agent.value.role === "admin" ? "Администратор" : "Агент";
});

const isFavorited = computed(() => {
  if (!property.value) return false;
  if (property.value.is_favorited) return true;
  return favorites.isFavorited(property.value.id);
});

const toggleFavorite = async () => {
  if (!property.value) return;
  if (!auth.isAuthenticated) {
    alert("Войдите, чтобы добавить в избранное.");
    router.push("/login");
    return;
  }
  try {
    await favorites.toggleFavorite(property.value);
  } catch (error) {
    alert("Не удалось обновить избранное. Попробуйте ещё раз.");
  }
};

const shareProperty = async () => {
  const url = window.location.href;
  try {
    await navigator.clipboard.writeText(url);
    showToast("Ссылка скопирована");
  } catch (error) {
    const textarea = document.createElement("textarea");
    textarea.value = url;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
    showToast("Ссылка скопирована");
  }
};

const startChat = async () => {
  if (!property.value) return;
  if (!auth.isAuthenticated) {
    alert("Войдите, чтобы написать агенту.");
    router.push("/login");
    return;
  }
  try {
    const conversation = await chat.startConversation(property.value.id);
    if (conversation?.id) {
      await router.push(`/dialogs/${conversation.id}`);
      window.scrollTo({ top: 0, left: 0, behavior: "auto" });
    }
  } catch (error) {
    alert("Не удалось создать диалог. Попробуйте ещё раз.");
  }
};

const propertyTypeLabel = computed(() => {
  const type = property.value?.property_type;
  if (!type) return "Объект";
  const mapping = {
    apartment: "Квартира",
    room: "Комната",
    house: "Дом",
    commercial: "Коммерческое помещение",
  };
  return mapping[type] || property.value?.building_type || "Объект";
});

const roomsLabel = computed(() => formatRooms(property.value?.rooms));
const areaLabel = computed(() => formatArea(property.value?.area_total));
const floorLabel = computed(() =>
  formatFloor(property.value?.floor, property.value?.floors_total)
);

const features = computed(() => {
  if (!property.value) return [];
  return [
    { label: "Тип недвижимости", value: propertyTypeLabel.value },
    { label: "Количество комнат", value: roomsLabel.value },
    { label: "Общая площадь", value: areaLabel.value },
    { label: "Жилая площадь", value: formatArea(property.value.living_area) },
    { label: "Площадь кухни", value: formatArea(property.value.kitchen_area) },
    ...(floorLabel.value ? [{ label: "Этаж", value: floorLabel.value }] : []),
    { label: "Год постройки", value: property.value.year_built || "—" },
    { label: "Тип дома", value: property.value.building_type || "—" },
    { label: "Новостройка", value: property.value.is_new_building ? "Да" : "Нет" },
  ];
});

const onSwiper = (swiper) => {
  swiperRef.value = swiper;
};

const onSlideChange = (swiper) => {
  activeSlide.value = swiper.activeIndex;
};

const goToSlide = (index) => {
  swiperRef.value?.slideTo(index);
  activeSlide.value = index;
};

const openLightbox = (index) => {
  lightboxIndex.value = index;
  lightboxVisible.value = true;
};

const fetchProperty = async () => {
  const { data } = await api.get(`/properties/${route.params.id}/`);
  property.value = data;
  const similarResponse = await api.get("/properties/", {
    params: { district: data.district, rooms: data.rooms, max_price: data.price * 1.2 },
  });
  const similarItems = Array.isArray(similarResponse.data)
    ? similarResponse.data
    : similarResponse.data?.results || [];
  similar.value = similarItems.filter((item) => item.id !== data.id).slice(0, 4);
};

onMounted(fetchProperty);
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;
@use "@/styles/mixins" as *;

.detail-breadcrumbs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  font-size: 0.9rem;
  color: $color-muted;
  margin-bottom: 1rem;

  a {
    color: inherit;
  }
}

.detail-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;

  h1 {
    @include heading-xl;
    margin: 0.5rem 0 0.3rem;
  }

  p {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: $color-muted;
  }

  &__meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    padding: 0;
    margin: 0.5rem 0 0;

    li {
      list-style: none;
      font-size: 0.9rem;
      color: $color-muted;
      background: rgba(15, 23, 42, 0.05);
      padding: 0.35rem 0.9rem;
      border-radius: $radius-sm;
    }
  }
}

.detail-header__actions {
  display: inline-flex;
  gap: 0.75rem;

  button {
    border: 1px solid rgba(15, 23, 42, 0.12);
    border-radius: $radius-lg;
    padding: 0.55rem 1rem;
    background: #fff;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    transition: background $transition-base, border-color $transition-base, color $transition-base;

    &.active {
      border-color: rgba(239, 68, 68, 0.4);
      color: #ef4444;
      background: rgba(239, 68, 68, 0.08);
    }
  }
}

.detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(0, 0.6fr);
  gap: 2rem;

  @include mobile {
    grid-template-columns: 1fr;
  }
}

.detail-gallery {
  position: relative;
  border-radius: $radius-lg;
  overflow: hidden;
  box-shadow: $shadow-card;

  img {
    width: 100%;
    height: clamp(320px, 45vw, 520px);
    object-fit: cover;
    cursor: zoom-in;
  }
}

.detail-gallery__thumbs {
  margin-top: 0.75rem;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;

  .thumb {
    width: 80px;
    height: 60px;
    border-radius: $radius-sm;
    overflow: hidden;
    border: 2px solid transparent;

    &.active {
      border-color: $color-primary;
    }

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
}

.photo-count {
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.4rem 0.8rem;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  z-index: 5;
}

.detail-info {
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.detail-info__mobile-price {
  display: none;
  @include mobile {
    display: block;
  }
}

.detail-description,
.detail-features,
.detail-map,
.detail-similar {
  @include card;
  padding: 1.5rem;
}

.detail-description p {
  line-height: 1.7;
  color: $color-muted;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;

  span {
    color: $color-muted;
    font-size: 0.85rem;
  }

  div {
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(15, 23, 42, 0.08);

    &:last-child {
      border-bottom: none;
    }

    strong {
      color: #0f172a;
      font-weight: 600;
    }
  }
}

.detail-map {
  display: flex;
  flex-direction: column;
  gap: 1rem;

  &__header {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
}

.detail-similar__list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.25rem;

  @include mobile {
    grid-template-columns: 1fr;
  }
}

.detail-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  position: sticky;
  top: 90px;
  align-self: flex-start;

  @include mobile {
    position: static;
  }
}

.contact-card {
  @include card;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;

  .agent {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.45rem;
    min-width: 0;

    strong,
    span {
      display: block;
      max-width: 100%;
      overflow-wrap: anywhere;
      word-break: break-word;
      line-height: 1.35;
    }

    strong {
      color: #0f172a;
      font-size: 1.05rem;
    }

    span {
      color: $color-muted;
      font-size: 0.85rem;
    }
  }
}

.loading-state {
  padding: 4rem 0;
}

.detail-toast {
  position: fixed;
  left: 50%;
  bottom: 1.5rem;
  transform: translateX(-50%);
  z-index: 120;
  padding: 0.85rem 1.2rem;
  border-radius: 999px;
  background: #0f172a;
  color: #fff;
  font-weight: 700;
  box-shadow: $shadow-hover;
}

@include mobile {
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .detail-header__actions {
    width: 100%;
    flex-direction: column;

    button {
      width: 100%;
      justify-content: center;
    }
  }

  .detail-gallery img {
    height: 260px;
  }

  .detail-map :deep(.re-map) {
    height: 55vh;
  }

  .feature-grid {
    grid-template-columns: 1fr;
  }
}
</style>
