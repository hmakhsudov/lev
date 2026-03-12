<template>
  <section class="favorites container">
    <header class="favorites__header">
      <div>
        <h1>Избранное</h1>
        <p class="text-muted">Ваши сохранённые объекты недвижимости.</p>
      </div>
      <RouterLink v-if="!isAuthenticated" to="/login" class="btn">Войти</RouterLink>
    </header>

    <div v-if="!isAuthenticated" class="favorites__empty">
      <h3>Войдите, чтобы видеть избранное</h3>
      <p class="text-muted">Добавляйте понравившиеся объекты в один клик.</p>
      <RouterLink to="/login" class="btn btn-primary">Перейти ко входу</RouterLink>
    </div>

    <div v-else>
      <div v-if="loading" class="favorites__grid">
        <SkeletonBlock v-for="n in 6" :key="n" height="280px" />
      </div>
      <div v-else-if="!favorites.length" class="favorites__empty">
        <h3>Пока пусто</h3>
        <p class="text-muted">Нажмите на сердечко у понравившегося объекта.</p>
        <RouterLink to="/" class="btn btn-primary">Посмотреть объекты</RouterLink>
      </div>
      <div v-else class="favorites__grid">
        <ListingCard v-for="item in favorites" :key="item.id" :property="item" layout="grid" />
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { RouterLink } from "vue-router";
import ListingCard from "@/components/ListingCard.vue";
import SkeletonBlock from "@/components/ui/SkeletonBlock.vue";
import { useAuthStore } from "@/store/auth";
import { useFavoritesStore } from "@/store/favorites";

const auth = useAuthStore();
const favoritesStore = useFavoritesStore();

const isAuthenticated = computed(() => auth.isAuthenticated);
const favorites = computed(() => favoritesStore.items);
const loading = computed(() => favoritesStore.loading);

onMounted(() => {
  if (auth.isAuthenticated) {
    favoritesStore.fetchFavorites().catch(() => null);
  }
});
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;
@use "@/styles/mixins" as *;

.favorites {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.favorites__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;

  @include mobile {
    flex-direction: column;
    align-items: flex-start;
  }
}

.favorites__grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.25rem;

  @include mobile {
    grid-template-columns: 1fr;
  }
}

.favorites__empty {
  @include card;
  padding: 2rem;
  display: grid;
  gap: 0.75rem;
  text-align: center;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.6rem 1.4rem;
  border-radius: 999px;
  border: 1px solid rgba(15, 23, 42, 0.1);
  color: $color-primary;
  font-weight: 600;
}

.btn-primary {
  background: $color-primary;
  color: #fff;
  border-color: transparent;
}

@include mobile {
  .btn {
    width: 100%;
  }
}
</style>
