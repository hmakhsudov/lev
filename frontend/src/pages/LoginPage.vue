<template>
  <div class="auth container">
    <section class="auth-card">
      <BaseChip icon="solar:login-2-line-duotone">Вход в аккаунт</BaseChip>
      <h1>Добро пожаловать</h1>
      <p class="text-muted">Используйте email и пароль, чтобы управлять подборками.</p>
      <form @submit.prevent="submit">
        <BaseField v-model="email" label="Email" icon="solar:letter-linear" type="email" required />
        <BaseField v-model="password" label="Пароль" icon="solar:lock-password-linear" type="password" required />
        <p v-if="auth.error" class="form-error">{{ auth.error }}</p>
        <BaseButton type="submit" icon="solar:login-3-line-duotone" block>Войти</BaseButton>
      </form>
      <RouterLink to="/register">Нет аккаунта? Зарегистрируйтесь</RouterLink>
    </section>
    <aside class="auth-aside">
      <img src="https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=900" alt="" />
      <div>
        <h3>Lev Estate</h3>
        <p>Цифровая витрина недвижимости с поддержкой AI.</p>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseChip from "@/components/ui/BaseChip.vue";
import BaseField from "@/components/ui/BaseField.vue";
import { useAuthStore } from "@/store/auth";

const email = ref("");
const password = ref("");
const auth = useAuthStore();
const router = useRouter();

const submit = async () => {
  const user = await auth.login({ email: email.value, password: password.value });
  if (user?.role === "admin") {
    router.push("/admin");
    return;
  }
  if (user?.role === "agent") {
    router.push("/agent");
    return;
  }
  router.push("/cabinet");
};
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;
@use "@/styles/mixins" as *;

.auth {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  align-items: center;
  gap: 2rem;

  @include mobile {
    grid-template-columns: 1fr;
  }
}

.auth-card {
  @include card;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;

  @include mobile {
    padding: 1.5rem;
  }
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-error {
  color: #dc2626;
  font-weight: 600;
}

.auth-aside {
  position: relative;
  border-radius: $radius-lg;
  overflow: hidden;
  min-height: 420px;
  isolation: isolate;

  @include mobile {
    display: none;
  }

  img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  div {
    position: absolute;
    left: 50%;
    right: auto;
    bottom: 1.25rem;
    width: min(360px, calc(100% - 2.5rem));
    transform: translateX(-50%);
    background: rgba(15, 23, 42, 0.72);
    color: #fff;
    padding: 1rem 1.25rem;
    border-radius: $radius-md;
    text-align: center;
    backdrop-filter: blur(10px);

    h3,
    p {
      margin: 0;
    }

    p {
      margin-top: 0.35rem;
      line-height: 1.45;
    }
  }
}
</style>
