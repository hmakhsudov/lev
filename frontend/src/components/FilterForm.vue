<template>
  <section class="filter-panel">
    <header>
      <div>
        <p class="filter-panel__title">Уточните параметры</p>
        <span>AI уже подобрал начальные фильтры, вы можете их изменить</span>
      </div>
      <BaseButton icon="solar:refresh-linear" variant="ghost" @click="$emit('reset')">Сбросить</BaseButton>
    </header>
    <div class="filter-panel__grid">
      <BaseField v-model="model.city" label="Город" icon="solar:buildings-bold" placeholder="Например, Санкт-Петербург" />
      <BaseField v-model="model.district" label="Район" icon="solar:map-point-bold" placeholder="Приморский" />
      <BaseField v-model.number="model.rooms" label="Комнат" icon="solar:bed-bold" type="number" min="1" />
      <label class="select-field">
        <span>Тип</span>
        <select v-model="model.property_type">
          <option value="">Любой</option>
          <option value="apartment">Квартира</option>
          <option value="room">Комната</option>
          <option value="house">Дом</option>
          <option value="commercial">Коммерция</option>
        </select>
        <Icon icon="solar:alt-arrow-down-bold" />
      </label>
      <BaseField v-model.number="model.min_price" label="Мин. цена" icon="solar:wallet-money-linear" type="number" placeholder="от" />
      <BaseField v-model.number="model.max_price" label="Макс. цена" icon="solar:wallet-outline" type="number" placeholder="до" />
      <BaseField v-model.number="model.area_min" label="Мин. площадь" icon="solar:ruler-cross-broken" type="number" />
      <BaseField v-model.number="model.area_max" label="Макс. площадь" icon="solar:ruler-cross-linear" type="number" />
    </div>
    <footer>
      <BaseButton icon="solar:filter-bold" @click="$emit('submit')">Показать объекты</BaseButton>
      <p class="text-muted">Работает фильтрация по цене, комнатам, району, типу и площади.</p>
    </footer>
  </section>
</template>

<script setup>
import { Icon } from "@iconify/vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseField from "@/components/ui/BaseField.vue";

const model = defineModel({ type: Object, default: () => ({}) });

defineEmits(["submit", "reset"]);
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;
@use "@/styles/mixins" as *;

.filter-panel {
  @include card;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;

  span {
    color: $color-muted;
    font-size: 0.88rem;
  }

  @include mobile {
    flex-direction: column;
    align-items: flex-start;
  }
}

.filter-panel__title {
  font-size: 1.1rem;
  font-weight: 700;
}

.filter-panel__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;

  @include mobile {
    grid-template-columns: 1fr;
  }
}

.select-field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;

  span {
    font-weight: 600;
    color: $color-muted;
  }

  select {
    appearance: none;
    padding: 0.75rem 1rem;
    border-radius: $radius-md;
    border: 1px solid rgba(15, 23, 42, 0.08);
    background: #fff;
  }

  svg {
    position: relative;
    top: -2.2rem;
    left: calc(100% - 2rem);
    pointer-events: none;
    color: $color-muted;
  }
}

footer {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;

  @include mobile {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
