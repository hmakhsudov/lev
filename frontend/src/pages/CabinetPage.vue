<template>
  <section class="cabinet container">
    <div class="cabinet__header">
      <div>
        <h1>Личный кабинет</h1>
        <p class="text-muted">Управляйте профилем и доступом к платформе.</p>
      </div>
      <BaseButton type="button" icon="solar:logout-2-bold" @click="handleLogout">Выйти</BaseButton>
    </div>

    <div class="cabinet__grid">
      <div class="card">
        <h3>Профиль</h3>
        <div class="profile-row">
          <span>Email</span>
          <strong>{{ user?.email || "—" }}</strong>
        </div>
        <div class="profile-row">
          <span>Роль</span>
          <strong>{{ roleLabel }}</strong>
        </div>
        <div class="profile-row">
          <span>Имя</span>
          <strong>{{ user?.first_name || "—" }}</strong>
        </div>
        <div class="profile-row">
          <span>Фамилия</span>
          <strong>{{ user?.last_name || "—" }}</strong>
        </div>
        <div class="profile-row">
          <span>Телефон</span>
          <strong>{{ user?.phone || "—" }}</strong>
        </div>
      </div>

      <div class="card">
        <h3>Редактировать профиль</h3>
        <p v-if="formError" class="form-error">{{ formError }}</p>
        <p v-if="formSuccess" class="form-success">{{ formSuccess }}</p>
        <BaseField v-model="form.first_name" label="Имя" :error="fieldErrors.first_name" />
        <BaseField v-model="form.last_name" label="Фамилия" :error="fieldErrors.last_name" />
        <BaseField v-model="form.phone" label="Телефон" :error="fieldErrors.phone" />
        <BaseButton :disabled="saving" type="button" @click="updateProfile">
          {{ saving ? "Сохраняем..." : "Сохранить" }}
        </BaseButton>
      </div>

      <div class="card">
        <h3>Доступы</h3>
        <p class="text-muted">
          При необходимости свяжитесь с менеджером для повышения роли и доступа к дополнительным функциям.
        </p>
        <div class="actions">
          <RouterLink v-if="isAgent" to="/admin" class="action-link">Панель агента</RouterLink>
          <RouterLink v-if="isAdmin" to="/admin" class="action-link">Админ панель</RouterLink>
          <RouterLink to="/" class="action-link">Вернуться к объектам</RouterLink>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseField from "@/components/ui/BaseField.vue";
import { useAuthStore } from "@/store/auth";

const auth = useAuthStore();
const router = useRouter();
const user = computed(() => auth.user);
const isAgent = computed(() => auth.isAgent);
const isAdmin = computed(() => auth.isAdmin);

const roleLabel = computed(() => {
  if (auth.isAdmin) return "Администратор";
  if (auth.isAgent) return "Агент";
  return "Пользователь";
});

const form = reactive({
  first_name: "",
  last_name: "",
  phone: "",
});
const fieldErrors = ref({});
const formError = ref("");
const formSuccess = ref("");
const saving = ref(false);

const syncForm = () => {
  form.first_name = user.value?.first_name || "";
  form.last_name = user.value?.last_name || "";
  form.phone = user.value?.phone || "";
};

const parseErrors = (error) => {
  const data = error?.response?.data;
  if (!data) return { message: "Не удалось обновить профиль.", fields: {} };
  if (data.detail) return { message: data.detail, fields: {} };
  if (typeof data === "object") {
    if (Array.isArray(data.non_field_errors) && data.non_field_errors.length) {
      return { message: data.non_field_errors[0], fields: {} };
    }
    const fields = {};
    Object.entries(data).forEach(([key, value]) => {
      if (Array.isArray(value)) fields[key] = value[0];
      else if (typeof value === "string") fields[key] = value;
    });
    return { message: "Проверьте поля формы.", fields };
  }
  return { message: "Не удалось обновить профиль.", fields: {} };
};

const updateProfile = async () => {
  formError.value = "";
  formSuccess.value = "";
  fieldErrors.value = {};
  saving.value = true;
  try {
    await auth.updateProfile({
      first_name: form.first_name,
      last_name: form.last_name,
      phone: form.phone,
    });
    formSuccess.value = "Профиль обновлён.";
    syncForm();
  } catch (error) {
    const parsed = parseErrors(error);
    formError.value = parsed.message;
    fieldErrors.value = parsed.fields;
  } finally {
    saving.value = false;
  }
};

const handleLogout = () => {
  auth.logout();
  router.push("/login");
};

onMounted(async () => {
  await auth.fetchCurrentUser();
  syncForm();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;
@use "@/styles/mixins" as *;

.cabinet {
  display: grid;
  gap: 2rem;
}

.cabinet__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;

  @include mobile {
    flex-direction: column;
    align-items: flex-start;
  }
}

.cabinet__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;

  @include mobile {
    grid-template-columns: 1fr;
  }
}

.card {
  @include card;
  padding: 1.75rem;
  display: grid;
  gap: 1rem;
}

.form-error {
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #b91c1c;
  padding: 0.6rem 0.8rem;
  border-radius: $radius-md;
}

.form-success {
  background: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.2);
  color: #166534;
  padding: 0.6rem 0.8rem;
  border-radius: $radius-md;
}

.profile-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
  padding-bottom: 0.5rem;

  @include mobile {
    flex-direction: column;
    align-items: flex-start;
  }
}

.actions {
  display: grid;
  gap: 0.75rem;
}

.action-link {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-radius: $radius-md;
  border: 1px solid rgba(15, 23, 42, 0.12);
  color: $color-primary;
  font-weight: 600;
  transition: background $transition-base, border-color $transition-base;

  &:hover {
    background: rgba(31, 117, 255, 0.08);
    border-color: rgba(31, 117, 255, 0.2);
  }
}
</style>
