<template>
  <div class="auth container">
    <section class="auth-card">
      <BaseChip icon="solar:login-2-line-duotone">Вход в аккаунт</BaseChip>
      <h1>Добро пожаловать</h1>
      <p class="text-muted">Используйте email и пароль, чтобы управлять подборками.</p>
      <form @submit.prevent="submit">
        <BaseField v-model="email" label="Email" icon="solar:letter-linear" type="email" required />
        <BaseField v-model="password" label="Пароль" icon="solar:lock-password-linear" type="password" required />
        <BaseButton type="submit" icon="solar:login-3-line-duotone" block>Войти</BaseButton>
      </form>
      <RouterLink to="/register">Нет аккаунта? Зарегистрируйтесь</RouterLink>
    </section>
    <aside class="auth-aside">
      <img src="https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=900" alt="" />
      <div>
        <h3>Lev Estate</h3>
        <p>Премиальная цифровая витрина недвижимости с поддержкой AI.</p>
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
  await auth.login({ email: email.value, password: password.value });
  router.push("/");
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
}

.auth-card {
  @include card;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.auth-aside {
  position: relative;
  border-radius: $radius-lg;
  overflow: hidden;
  min-height: 420px;

  img {
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  div {
    position: absolute;
    bottom: 1rem;
    left: 1rem;
    background: rgba(0, 0, 0, 0.4);
    color: #fff;
    padding: 1rem;
    border-radius: $radius-md;
  }
}
</style>
