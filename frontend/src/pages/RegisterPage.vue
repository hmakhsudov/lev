<template>
  <div class="auth container">
    <section class="auth-card">
      <BaseChip icon="solar:user-plus-linear">Регистрация</BaseChip>
      <h1>Создайте аккаунт</h1>
      <p class="text-muted">Выберите роль: покупатель или агент.</p>
      <form @submit.prevent="submit">
        <BaseField v-model="email" label="Email" icon="solar:letter-bold" type="email" required />
        <BaseField v-model="password" label="Пароль" icon="solar:lock-password-bold" type="password" required />
        <BaseField v-model="passwordConfirm" label="Подтверждение пароля" icon="solar:lock-keyhole-linear" type="password" required />
        <label class="select-field">
          <span>Роль</span>
          <select v-model="role">
            <option value="user">Покупатель</option>
            <option value="agent">Агент</option>
          </select>
        </label>
        <p v-if="auth.error" class="form-error">{{ auth.error }}</p>
        <BaseButton type="submit" icon="solar:user-rounded-plus-outline" block>Создать</BaseButton>
      </form>
      <RouterLink to="/login">Уже есть аккаунт? Войти</RouterLink>
    </section>
    <aside class="auth-aside">
      <img src="https://images.unsplash.com/photo-1493666438817-866a91353ca9?w=900" alt="" />
      <div>
        <h3>Команда Lev</h3>
        <p>Сопровождаем сделки и автоматизируем подбор.</p>
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
const passwordConfirm = ref("");
const role = ref("user");
const auth = useAuthStore();
const router = useRouter();

const submit = async () => {
  await auth.register({
    email: email.value,
    password: password.value,
    password_confirm: passwordConfirm.value,
    role: role.value,
  });
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

.select-field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;

  select {
    padding: 0.75rem 1rem;
    border-radius: $radius-md;
    border: 1px solid rgba(15, 23, 42, 0.12);
  }
}

.auth-aside {
  position: relative;
  border-radius: $radius-lg;
  overflow: hidden;
  min-height: 420px;

  @include mobile {
    display: none;
  }

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
