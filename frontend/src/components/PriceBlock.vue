<template>
  <section class="price-card">
    <div>
      <p class="price-card__value">{{ formatPrice(property.price) }}</p>
      <p v-if="property.area_total" class="price-card__sub">≈ {{ pricePerMeter }}</p>
      <p v-if="priceStatus.label" class="price-card__hint" :class="priceStatus.class">
        Прогнозируемая цена: {{ formatPrice(property.predicted_price) }} — {{ priceStatus.hint }}
      </p>
    </div>
    <div class="price-card__stats">
      <div>
        <span>Комнат</span>
        <strong>{{ roomsLabel }}</strong>
      </div>
      <div>
        <span>Площадь</span>
        <strong>{{ areaLabel }}</strong>
      </div>
      <div>
        <span>Этаж</span>
        <strong>{{ floorLabel }}</strong>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";

import { formatArea, formatFloor, formatPrice, formatRooms, safeNumber } from "@/utils/formatters";

const props = defineProps({
  property: { type: Object, required: true },
  priceStatus: { type: Object, required: true },
});

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
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;
@use "@/styles/mixins" as *;

.price-card {
  @include card;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;

  &__value {
    font-size: 2rem;
    font-weight: 700;
    color: $color-primary;
  }

  &__sub {
    color: $color-muted;
  }

  &__hint {
    font-size: 0.9rem;

    &.is-good {
      color: $color-success;
    }

    &.is-risk {
      color: $color-warning;
    }
  }

  &__stats {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;

    div {
      flex: 1;
      min-width: 120px;
      background: rgba(15, 23, 42, 0.05);
      padding: 0.75rem;
      border-radius: $radius-md;

      span {
        font-size: 0.75rem;
        color: $color-muted;
      }

      strong {
        display: block;
        font-size: 1.1rem;
      }
    }
  }
}
</style>
