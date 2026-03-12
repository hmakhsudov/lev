<template>
  <section class="dialogs container">
    <header class="dialogs__header">
      <div>
        <h1>Диалоги</h1>
        <p class="text-muted">Общайтесь с агентами по выбранным объектам.</p>
      </div>
      <RouterLink v-if="!isAuthenticated" to="/login" class="btn">Войти</RouterLink>
    </header>

    <div v-if="!isAuthenticated" class="dialogs__empty">
      <h3>Войдите, чтобы читать сообщения</h3>
      <p class="text-muted">Диалоги доступны только авторизованным пользователям.</p>
      <RouterLink to="/login" class="btn btn-primary">Перейти ко входу</RouterLink>
    </div>

    <div v-else>
      <div v-if="loading" class="dialogs__list">
        <SkeletonBlock v-for="n in 6" :key="n" height="84px" />
      </div>
      <div v-else-if="!conversations.length" class="dialogs__empty">
        <h3>Пока нет диалогов</h3>
        <p class="text-muted">Напишите агенту на странице объекта.</p>
        <RouterLink to="/" class="btn btn-primary">К объектам</RouterLink>
      </div>
      <div v-else class="dialogs__list">
        <button
          v-for="item in conversations"
          :key="item.id"
          class="dialog-card"
          type="button"
          @click="openDialog(item.id)"
        >
          <img :src="item.listing.main_image || fallbackImage" alt="" />
          <div class="dialog-card__body">
            <div class="dialog-card__top">
              <strong>{{ item.listing.title || "Объект недвижимости" }}</strong>
              <span>{{ formatTime(item.last_message_at) }}</span>
            </div>
            <p class="dialog-card__meta">
              {{ item.listing.address || item.listing.city }}
            </p>
            <p class="dialog-card__preview">
              {{ item.last_message?.text || "Сообщений пока нет" }}
            </p>
          </div>
          <div class="dialog-card__aside">
            <span class="dialog-card__price">{{ formatPrice(item.listing.price) }}</span>
            <span class="dialog-card__user">{{ participantName(item.other_participant) }}</span>
          </div>
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { RouterLink, useRouter } from "vue-router";
import SkeletonBlock from "@/components/ui/SkeletonBlock.vue";
import { useAuthStore } from "@/store/auth";
import { useChatStore } from "@/store/chat";
import { formatPrice } from "@/utils/formatters";

const auth = useAuthStore();
const chat = useChatStore();
const router = useRouter();
const fallbackImage =
  "https://images.unsplash.com/photo-1505693314120-0d443867891c?w=600&auto=format&fit=crop";

const isAuthenticated = computed(() => auth.isAuthenticated);
const conversations = computed(() => chat.conversations);
const loading = computed(() => chat.loading);

const participantName = (user) => {
  if (!user) return "Собеседник";
  const full = [user.first_name, user.last_name].filter(Boolean).join(" ");
  return full || user.email || "Собеседник";
};

const formatTime = (value) => {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleString("ru-RU", { hour: "2-digit", minute: "2-digit" });
};

const openDialog = (id) => {
  router.push(`/dialogs/${id}`);
};

onMounted(() => {
  if (auth.isAuthenticated) {
    chat.fetchConversations().catch(() => null);
  }
});
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;
@use "@/styles/mixins" as *;

.dialogs {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

.dialogs__header {
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

.dialogs__list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.dialogs__empty {
  @include card;
  padding: 2rem;
  display: grid;
  gap: 0.75rem;
  text-align: center;
}

.dialog-card {
  @include card;
  display: grid;
  grid-template-columns: 72px 1fr auto;
  gap: 1rem;
  padding: 1rem;
  align-items: center;
  text-align: left;
  cursor: pointer;
  border: none;
  background: #fff;
  transition: transform $transition-base, box-shadow $transition-base;

  &:hover {
    transform: translateY(-2px);
    box-shadow: $shadow-hover;
  }

  img {
    width: 72px;
    height: 72px;
    border-radius: 12px;
    object-fit: cover;
  }
}

.dialog-card__body {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.dialog-card__top {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  color: $color-muted;

  strong {
    color: #0f172a;
  }
}

.dialog-card__meta {
  color: $color-muted;
  font-size: 0.9rem;
}

.dialog-card__preview {
  color: #0f172a;
  font-size: 0.95rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.dialog-card__aside {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  align-items: flex-end;
}

.dialog-card__price {
  font-weight: 700;
  color: $color-primary;
}

.dialog-card__user {
  color: $color-muted;
  font-size: 0.85rem;
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
  .dialog-card {
    grid-template-columns: 1fr;
    text-align: left;

    img {
      width: 100%;
      height: 160px;
    }
  }

  .dialog-card__aside {
    align-items: flex-start;
  }

  .btn {
    width: 100%;
  }
}
</style>
