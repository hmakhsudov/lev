<template>
  <article
    class="listing-card"
    v-motion
    :initial="{ opacity: 0, y: 30 }"
    :enter="{ opacity: 1, y: 0, transition: { duration: 0.35 } }"
  >
    <div class="listing-card__media">
      <div class="listing-card__favorite">
        <Icon icon="solar:heart-linear" width="20" />
      </div>
      <div v-if="gallery.length > 1" class="listing-card__photo-count">
        <Icon icon="solar:camera-line-duotone" width="18" />
        <span>{{ gallery.length }} фото</span>
      </div>
      <div class="listing-card__badges">
        <BaseChip :icon="property.is_new_building ? 'solar:city-bold' : 'solar:home-2-bold'">
          {{ property.is_new_building ? "Новостройка" : "Вторичка" }}
        </BaseChip>
        <BaseChip v-if="priceStatus.label" :variant="priceStatus.variant" icon="solar:discount-shape-linear">
          {{ priceStatus.label }}
        </BaseChip>
      </div>
      <div class="listing-card__media-inner">
        <img :src="previewImage" :alt="property.title || 'Объект недвижимости'" @error="onImageError" />
        <div class="listing-card__media-overlay">
          <RouterLink :to="`/property/${property.id}`">
            Подробнее
            <Icon icon="solar:arrow-right-up-linear" width="18" />
          </RouterLink>
        </div>
      </div>
    </div>

    <div class="listing-card__content">
      <header class="listing-card__header">
        <p class="listing-card__price">{{ formatPrice(property.price) }}</p>
        <p v-if="property.area_total" class="listing-card__price-sub">≈ {{ pricePerMeter }}</p>
        <p v-if="property.predicted_price" class="listing-card__price-hint" :class="priceStatus.class">
          Прогнозируемая цена: {{ formatPrice(property.predicted_price) }} — {{ priceStatus.hint }}
        </p>
      </header>

      <h3 class="listing-card__title">{{ property.title || "Объект недвижимости" }}</h3>

      <div class="listing-card__info">
        <div class="info-pill">
          <Icon icon="solar:bed-linear" width="18" />
          <span>{{ roomsLabel }}</span>
        </div>
        <div class="info-pill">
          <Icon icon="solar:ruler-cross-linear" width="18" />
          <span>{{ areaLabel }}</span>
        </div>
        <div class="info-pill">
          <Icon icon="solar:buildings-2-linear" width="18" />
          <span>{{ floorLabel }}</span>
        </div>
        <div class="info-pill">
          <Icon icon="solar:city-linear" width="18" />
          <span>{{ typeLabel }}</span>
        </div>
      </div>

      <div class="listing-card__location">
        <Icon icon="solar:map-point-outline" width="22" />
        <div>
          <strong>{{ locationLine }}</strong>
          <p>{{ property.address || "Адрес уточняется" }}</p>
        </div>
      </div>

      <div class="listing-card__actions">
        <RouterLink :to="`/property/${property.id}`" class="btn btn-primary">
          <Icon icon="solar:arrow-right-up-linear" width="18" />
          Подробнее
        </RouterLink>
        <button class="btn btn-ghost" @click="$emit('focus-map', property)">
          <Icon icon="solar:pin-outline" width="18" />
          На карте
        </button>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { RouterLink } from "vue-router";
import { Icon } from "@iconify/vue";

import BaseChip from "@/components/ui/BaseChip.vue";
import { formatArea, formatFloor, formatPrice, formatRooms, safeNumber } from "@/utils/formatters";

const props = defineProps({
  property: { type: Object, required: true },
});

defineEmits(["focus-map"]);

const fallbackImage =
  "https://images.unsplash.com/photo-1505693314120-0d443867891c?w=900&auto=format&fit=crop";
const previewImage = ref(fallbackImage);

const gallery = computed(() => {
  const raw = props.property.images?.length ? props.property.images : [];
  const unique = [...new Set([props.property.main_image, ...raw].filter(Boolean))];
  return unique.length ? unique : [fallbackImage];
});

watch(
  gallery,
  (list) => {
    previewImage.value = list[0] || fallbackImage;
  },
  { immediate: true }
);

const onImageError = () => {
  previewImage.value = fallbackImage;
};

const pricePerMeter = computed(() => {
  const price = safeNumber(props.property.price);
  const area = safeNumber(props.property.area_total);
  if (!price || !area) return "—";
  return `${Math.round(price / area).toLocaleString("ru-RU")} ₽ за м²`;
});

const roomsLabel = computed(() => formatRooms(props.property.rooms));

const areaLabel = computed(() => formatArea(props.property.area_total));

const floorLabel = computed(() =>
  formatFloor(props.property.floor, props.property.floors_total)
);

const typeLabel = computed(() => {
  if (props.property.property_type === "apartment") return "Квартира";
  if (props.property.property_type === "room") return "Комната";
  if (props.property.property_type === "house") return "Дом";
  if (props.property.property_type === "commercial") return "Коммерческая";
  return props.property.building_type || "Объект";
});

const locationLine = computed(() => {
  const city = props.property.city || "Город уточняется";
  const district = props.property.district ? props.property.district : "";
  return district ? `${city}, ${district}` : city;
});

const priceStatus = computed(() => {
  const predicted = safeNumber(props.property.predicted_price);
  const price = safeNumber(props.property.price);
  if (!predicted || !price) return { label: "", hint: "", variant: "neutral", class: "" };
  if (predicted > price) {
    return {
      label: "Выгодное предложение",
      hint: "Цена ниже ожидаемой",
      variant: "success",
      class: "is-good",
    };
  }
  if (predicted < price) {
    return {
      label: "Цена выше рынка",
      hint: "Есть простор для переговоров",
      variant: "warning",
      class: "is-risk",
    };
  }
  return { label: "Рыночная цена", hint: "Соответствует прогнозу", variant: "neutral", class: "" };
});
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;

.listing-card {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 1.5rem;
  padding: 1.5rem;
  background: #fff;
  border-radius: $radius-lg;
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: $shadow-card;
  transition: transform $transition-base, box-shadow $transition-base;

  &:hover {
    transform: translateY(-4px);
    box-shadow: $shadow-hover;
  }

  @media (max-width: 1100px) {
    grid-template-columns: 1fr;
  }
}

.listing-card__media {
  position: relative;

  &-inner {
    border-radius: $radius-lg;
    overflow: hidden;
    position: relative;

    img {
      width: 100%;
      height: 280px;
      object-fit: cover;
      transition: transform $transition-base;
    }
  }

  &:hover img {
    transform: scale(1.04);
  }
}

.listing-card__media-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent, rgba(0, 0, 0, 0.55));
  opacity: 0;
  display: flex;
  justify-content: flex-end;
  align-items: flex-end;
  padding: 1rem;
  transition: opacity $transition-base;

  a {
    color: #fff;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-weight: 600;
  }
}

.listing-card__media:hover .listing-card__media-overlay {
  opacity: 1;
}

.listing-card__favorite {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  color: $color-muted;
  z-index: 5;
  box-shadow: $shadow-soft;
}

.listing-card__photo-count {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  z-index: 5;
  font-size: 0.85rem;
}

.listing-card__badges {
  position: absolute;
  top: 1rem;
  left: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  z-index: 5;
}

.listing-card__content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.listing-card__price {
  font-size: 1.5rem;
  font-weight: 700;
  color: $color-primary;
}

.listing-card__price-sub {
  color: $color-muted;
  font-size: 0.9rem;
}

.listing-card__price-hint {
  font-size: 0.9rem;
  color: $color-muted;

  &.is-good {
    color: $color-success;
  }
  &.is-risk {
    color: $color-warning;
  }
}

.listing-card__title {
  font-size: 1.1rem;
  font-weight: 600;
}

.listing-card__info {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.info-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.9rem;
  border-radius: $radius-sm;
  background: rgba(15, 23, 42, 0.06);
  font-size: 0.9rem;
}

.listing-card__location {
  display: flex;
  gap: 0.75rem;
  color: $color-muted;

  strong {
    color: #0f172a;
  }

  p {
    margin: 0;
  }
}

.listing-card__actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn {
  border: none;
  border-radius: $radius-lg;
  padding: 0.65rem 1.3rem;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 600;
  cursor: pointer;
  transition: background $transition-base, color $transition-base, box-shadow $transition-base;
}

.btn-primary {
  background: linear-gradient(135deg, $color-primary, #7c9bff);
  color: #fff;
  box-shadow: $shadow-soft;

  &:hover {
    box-shadow: $shadow-hover;
  }
}

.btn-ghost {
  background: rgba(15, 23, 42, 0.06);
  color: #0f172a;
}

@media (max-width: 768px) {
  .listing-card__media img {
    height: 220px;
  }
}
</style>
