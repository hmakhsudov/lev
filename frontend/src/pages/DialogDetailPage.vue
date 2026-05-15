<template>
  <section class="dialog container">
    <header class="dialog__header" v-if="conversation">
      <button class="dialog__back" type="button" @click="goBack">← К диалогам</button>
      <div>
        <h1>{{ conversation.listing.title || "Объект недвижимости" }}</h1>
        <p class="text-muted">
          {{ participantName(conversation.other_participant) }} · {{ conversation.listing.address || conversation.listing.city }}
        </p>
      </div>
      <RouterLink :to="`/property/${conversation.listing.id}`" class="dialog__link">
        Перейти к объекту
      </RouterLink>
    </header>

    <div v-if="loading" class="dialog__loading">
      <SkeletonBlock height="420px" />
    </div>
    <div v-else class="dialog__body">
      <div class="messages" ref="messagesRef">
        <div
          v-for="msg in messages"
          :key="msg.id"
          :class="['message', { 'message--me': msg.sender?.id === userId }]"
        >
          <div class="message__bubble">
            <p>{{ msg.text }}</p>
            <span>{{ formatTime(msg.created_at) }}</span>
          </div>
        </div>
      </div>
      <form class="composer" @submit.prevent="handleSend">
        <input v-model="draft" type="text" placeholder="Напишите сообщение..." />
        <button type="submit" :disabled="!draft.trim()">Отправить</button>
      </form>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import SkeletonBlock from "@/components/ui/SkeletonBlock.vue";
import { useAuthStore } from "@/store/auth";
import { useChatStore } from "@/store/chat";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const chat = useChatStore();

const draft = ref("");
const messagesRef = ref(null);

const conversation = computed(() => chat.activeConversation);
const messages = computed(() => chat.messages);
const loading = computed(() => chat.loading);
const userId = computed(() => auth.user?.id);

const participantName = (user) => {
  if (!user) return "Собеседник";
  const full = [user.first_name, user.last_name].filter(Boolean).join(" ");
  return full || user.email || "Собеседник";
};

const formatTime = (value) => {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
  }
};

const handleSend = async () => {
  const text = draft.value.trim();
  if (!text) return;
  draft.value = "";
  await chat.sendMessage(text);
  scrollToBottom();
};

const goBack = () => {
  router.push("/dialogs");
};

watch(messages, () => scrollToBottom(), { deep: true });

const loadDialog = async () => {
  if (!auth.isAuthenticated) {
    router.push("/login");
    return;
  }
  const id = route.params.id;
  if (!id) return;
  await chat.openConversation(id);
  scrollToBottom();
};

watch(
  () => route.params.id,
  () => loadDialog()
);

onMounted(async () => {
  window.scrollTo({ top: 0, left: 0, behavior: "auto" });
  await loadDialog();
});

onBeforeUnmount(() => {
  chat.closeSocket();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;
@use "@/styles/mixins" as *;

.dialog {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.dialog__header {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 1rem;

  h1 {
    margin: 0;
  }
}

.dialog__back {
  border: none;
  background: rgba(15, 23, 42, 0.06);
  border-radius: 999px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-weight: 600;
}

.dialog__link {
  border: 1px solid rgba(15, 23, 42, 0.1);
  border-radius: 999px;
  padding: 0.5rem 1rem;
  color: $color-primary;
  font-weight: 600;
}

.dialog__body {
  @include card;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-height: 65vh;
}

.messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.5rem;
}

.message {
  display: flex;
  justify-content: flex-start;
}

.message--me {
  justify-content: flex-end;

  .message__bubble {
    background: $color-primary;
    color: #fff;
  }

  span {
    color: rgba(255, 255, 255, 0.8);
  }
}

.message__bubble {
  max-width: 70%;
  background: rgba(15, 23, 42, 0.06);
  border-radius: 16px;
  padding: 0.75rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.95rem;

  p {
    margin: 0;
  }

  span {
    font-size: 0.75rem;
    color: $color-muted;
    align-self: flex-end;
  }
}

.composer {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 0.75rem;

  input {
    border-radius: 999px;
    border: 1px solid rgba(15, 23, 42, 0.1);
    padding: 0.75rem 1rem;
  }

  button {
    border: none;
    border-radius: 999px;
    padding: 0.75rem 1.5rem;
    background: $color-primary;
    color: #fff;
    font-weight: 600;
    cursor: pointer;
  }
}

@include mobile {
  .dialog__header {
    grid-template-columns: 1fr;
  }

  .composer {
    position: sticky;
    bottom: 0;
    background: #fff;
    padding-top: 0.5rem;
    grid-template-columns: 1fr;

    button {
      width: 100%;
    }
  }
}
</style>
