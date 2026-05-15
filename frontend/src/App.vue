<template>
  <div class="app-shell">
    <header class="app-shell__header" :class="{ 'app-shell__header--scrolled': scrolled }">
      <div class="container header__content">
        <RouterLink to="/" class="brand">
          <div>
            <p>LEV ESTATE</p>
            <small>AI недвижимость</small>
          </div>
        </RouterLink>
        <nav>
          <RouterLink to="/" data-hint="Каталог объектов, фильтры и карта">Объекты</RouterLink>
          <RouterLink to="/assistant" data-hint="Подбор недвижимости по текстовому запросу">AI ассистент</RouterLink>
          <RouterLink to="/favorites" data-hint="Сохранённые объекты">
            Избранное
            <span v-if="favoritesCount" class="badge">{{ favoritesCount }}</span>
          </RouterLink>
          <RouterLink v-if="isAuthenticated" to="/dialogs" data-hint="Переписка с агентами и клиентами">Диалоги</RouterLink>
          <RouterLink v-if="isAdmin" to="/admin" data-hint="Объекты, агенты и управление сайтом">Админ панель</RouterLink>
          <RouterLink v-else-if="isAgent" to="/agent" data-hint="Создание и редактирование ваших объектов">Панель агента</RouterLink>
        </nav>
        <div class="header__actions">
          <template v-if="isAuthenticated">
            <RouterLink to="/cabinet" class="ghost">Личный кабинет</RouterLink>
            <button class="accent" type="button" @click="logout">Выйти</button>
          </template>
          <template v-else>
            <RouterLink to="/login" class="ghost">Войти</RouterLink>
            <RouterLink to="/register" class="accent">Регистрация</RouterLink>
          </template>
        </div>
        <button class="header__menu" @click="menuOpen = !menuOpen">
          <Icon icon="solar:hamburger-menu-linear" width="28" />
        </button>
      </div>
      <transition name="fade">
        <div v-if="menuOpen" class="mobile-nav">
          <RouterLink to="/" @click="menuOpen = false">Объекты</RouterLink>
          <RouterLink to="/assistant" @click="menuOpen = false">AI ассистент</RouterLink>
          <RouterLink to="/favorites" @click="menuOpen = false">
            Избранное
            <span v-if="favoritesCount" class="badge">{{ favoritesCount }}</span>
          </RouterLink>
          <RouterLink v-if="isAuthenticated" to="/dialogs" @click="menuOpen = false">Диалоги</RouterLink>
          <RouterLink v-if="isAdmin" to="/admin" @click="menuOpen = false">Админ панель</RouterLink>
          <RouterLink v-else-if="isAgent" to="/agent" @click="menuOpen = false">Панель агента</RouterLink>
          <RouterLink v-if="isAuthenticated" to="/cabinet" @click="menuOpen = false">Личный кабинет</RouterLink>
          <button v-if="isAuthenticated" type="button" class="ghost" @click="handleLogout">Выйти</button>
          <template v-else>
            <RouterLink to="/login" @click="menuOpen = false">Войти</RouterLink>
            <RouterLink to="/register" @click="menuOpen = false">Регистрация</RouterLink>
          </template>
        </div>
      </transition>
    </header>

    <main class="app-shell__main">
      <RouterView />
    </main>

    <footer class="app-shell__footer">
      <div class="container footer__inner">
        <p>© {{ new Date().getFullYear() }} Lev Estate. Все права защищены.</p>
        <div>
          <a href="mailto:info@lev.estate">info@lev.estate</a>
          <span>+7 (812) 000-00-00</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { Icon } from "@iconify/vue";
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useAuthStore } from "@/store/auth";
import { useFavoritesStore } from "@/store/favorites";
import { useChatStore } from "@/store/chat";
import { useRouter } from "vue-router";

const scrolled = ref(false);
const menuOpen = ref(false);
const auth = useAuthStore();
const favorites = useFavoritesStore();
const chat = useChatStore();
const router = useRouter();

const isAuthenticated = computed(() => auth.isAuthenticated);
const isAdmin = computed(() => auth.isAdmin);
const isAgent = computed(() => auth.isAgent);
const favoritesCount = computed(() => favorites.count);

const logout = () => {
  auth.logout();
  favorites.reset();
  chat.reset();
  router.push("/login");
};

const handleLogout = () => {
  menuOpen.value = false;
  logout();
};

const onScroll = () => {
  scrolled.value = window.scrollY > 30;
};

onMounted(() => {
  auth.init();
  if (auth.isAuthenticated) {
    favorites.fetchFavorites().catch(() => null);
  }
  window.addEventListener("scroll", onScroll);
});

watch(isAuthenticated, (value) => {
  if (value) {
    favorites.fetchFavorites().catch(() => null);
    chat.fetchConversations().catch(() => null);
  } else {
    favorites.reset();
    chat.reset();
  }
});
onUnmounted(() => window.removeEventListener("scroll", onScroll));
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;
@use "@/styles/mixins" as *;

.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-shell__header {
  position: sticky;
  top: 0;
  width: 100%;
  z-index: 50;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(15, 23, 42, 0.07);
  transition: box-shadow $transition-base;

  &--scrolled {
    box-shadow: $shadow-soft;
  }
}

.header__content {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem 0;

  @include mobile {
    gap: 0.75rem;
    padding: 0.75rem 0;
  }

  nav {
    margin-left: auto;
    display: flex;
    gap: 1rem;

    a {
      position: relative;
      color: $color-muted;
      padding: 0.5rem 0.8rem;
      border-radius: $radius-sm;
      transition: color $transition-base, background $transition-base;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;

      &.router-link-active,
      &:hover {
        color: $color-primary;
        background: rgba(31, 117, 255, 0.1);
      }

      &::after {
        content: attr(data-hint);
        position: absolute;
        left: 50%;
        top: calc(100% + 0.65rem);
        transform: translate(-50%, -4px);
        width: max-content;
        max-width: 240px;
        padding: 0.55rem 0.75rem;
        border-radius: $radius-md;
        background: #0f172a;
        color: #fff;
        font-size: 0.78rem;
        line-height: 1.3;
        box-shadow: $shadow-hover;
        opacity: 0;
        pointer-events: none;
        transition: opacity $transition-base, transform $transition-base;
        z-index: 80;
        text-align: center;
        white-space: normal;
      }

      &:hover::after,
      &:focus-visible::after {
        opacity: 1;
        transform: translate(-50%, 0);
      }
    }

    @include mobile {
      display: none;
    }
  }
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  font-weight: 600;
  color: #111827;

  img {
    display: none;
  }

  small {
    display: block;
    font-size: 0.7rem;
    color: $color-muted;
    letter-spacing: 0.2em;
  }
}

.header__actions {
  display: flex;
  gap: 0.75rem;

  a,
  button {
    padding: 0.55rem 1.4rem;
    border-radius: 999px;
    font-weight: 600;
    transition: transform $transition-base, box-shadow $transition-base;
    box-shadow: $shadow-soft;
    border: none;
    cursor: pointer;

    &.ghost {
      background: #fff;
      color: $color-muted;
      border: 1px solid rgba(15, 23, 42, 0.08);
    }

    &.accent {
      background: $color-primary;
      color: #fff;
    }

    &:hover {
      transform: translateY(-2px);
      box-shadow: $shadow-hover;
    }
  }

  @include mobile {
    display: none;
  }
}

.header__menu {
  margin-left: auto;
  border: none;
  background: none;
  display: none;

  @include mobile {
    display: block;
    color: $color-primary;
  }
}

.mobile-nav {
  display: none;
  flex-direction: column;
  padding: 1rem;
  gap: 0.5rem;
  background: #fff;
  border-top: 1px solid rgba(15, 23, 42, 0.06);

  a {
    padding: 0.8rem 1rem;
    background: #fff;
    border-radius: $radius-sm;
    box-shadow: $shadow-soft;
  }

  button {
    padding: 0.8rem 1rem;
    background: #fff;
    border-radius: $radius-sm;
    border: none;
    text-align: left;
    box-shadow: $shadow-soft;
    cursor: pointer;
  }

  @include mobile {
    display: flex;
  }
}

.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 999px;
  background: $color-primary;
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
}

.app-shell__main {
  flex: 1;
  padding: 2rem 0 4rem;

  @include mobile {
    padding: 1.5rem 0 3rem;
  }
}

.app-shell__footer {
  background: #0f172a;
  color: #fff;
  padding: 2rem 0;
}

.footer__inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  font-size: 0.95rem;

  a {
    color: rgba(255, 255, 255, 0.8);
  }

  @include mobile {
    flex-direction: column;
    text-align: center;
  }
}
</style>
