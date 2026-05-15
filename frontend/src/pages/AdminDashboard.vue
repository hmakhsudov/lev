<template>
  <div class="admin container">
    <header class="admin__header">
      <div>
        <BaseChip icon="solar:shield-check-bold">{{ panelBadge }}</BaseChip>
        <h1>{{ panelTitle }}</h1>
        <p class="text-muted">{{ panelDescription }}</p>
      </div>
      <div class="admin__actions">
        <!-- <BaseButton icon="solar:database-linear" variant="secondary" @click="syncCian">Синхронизировать CIAN</BaseButton>
        <BaseButton icon="solar:compass-linear" variant="ghost" @click="geocode">Геокодировать</BaseButton> -->
      </div>
    </header>

    <section class="admin__grid">
      <form v-if="canManage" class="form" @submit.prevent="saveProperty">
        <h2>{{ editingId ? "Редактировать объект" : "Создать объект" }}</h2>
        <p v-if="editingId" class="form__edit-note">
          Вы редактируете существующий объект. Если новые фотографии не выбраны, текущие фотографии сохранятся.
        </p>
        <p v-if="formError" class="form__error">{{ formError }}</p>
        <p v-if="successMessage" class="form__success">{{ successMessage }}</p>
        <ul v-if="Object.keys(fieldErrors).length" class="form__errors">
          <li v-for="(msg, key) in fieldErrors" :key="key">
            {{ fieldLabel(key) }}: {{ msg }}
          </li>
        </ul>
        <div class="form__section">
          <h3>Основное</h3>
          <div class="form__grid">
            <BaseField v-model="form.title" label="Название" icon="solar:home-add-linear" required :error="fieldErrors.title" />
            <BaseField
              v-model.number="form.price"
              label="Цена"
              icon="solar:wallet-linear"
              type="number"
              required
              :error="fieldErrors.price"
            />
            <BaseField v-model="form.city" label="Город" icon="solar:map-point-line-duotone" required :error="fieldErrors.city" />
            <BaseField
              v-model="form.address"
              label="Адрес"
              icon="solar:map-point-line-duotone"
              required
              :error="fieldErrors.address"
            />
            <BaseField v-model="form.district" label="Район" icon="solar:map-point-favourite-bold" :error="fieldErrors.district" />
          </div>
          <label class="select-field">
            <span>Тип объекта</span>
            <select v-model="form.property_type">
              <option value="apartment">Квартира</option>
              <option value="room">Комната</option>
              <option value="house">Дом</option>
              <option value="commercial">Коммерция</option>
            </select>
          </label>
          <BaseField
            v-model="form.description"
            label="Описание"
            icon="solar:document-text-linear"
            tag="textarea"
            rows="4"
          />
        </div>

        <div class="form__section">
          <h3>Параметры</h3>
          <div class="form__grid">
            <BaseField
              v-model.number="form.rooms"
              label="Комнат"
              icon="solar:bed-linear"
              type="number"
              min="0"
              :error="fieldErrors.rooms"
            />
            <BaseField
              v-model.number="form.area_total"
              label="Площадь общая"
              icon="solar:ruler-linear"
              type="number"
              step="0.1"
              :error="fieldErrors.area_total"
            />
            <BaseField
              v-model.number="form.living_area"
              label="Площадь жилая"
              icon="solar:ruler-linear"
              type="number"
              step="0.1"
              :error="fieldErrors.living_area"
            />
            <BaseField
              v-model.number="form.kitchen_area"
              label="Площадь кухни"
              icon="solar:ruler-linear"
              type="number"
              step="0.1"
              :error="fieldErrors.kitchen_area"
            />
            <BaseField
              v-model.number="form.floor"
              label="Этаж"
              icon="solar:buildings-2-linear"
              type="number"
              :error="fieldErrors.floor"
            />
            <BaseField
              v-model.number="form.floors_total"
              label="Этажей в доме"
              icon="solar:buildings-linear"
              type="number"
              :error="fieldErrors.floors_total"
            />
            <BaseField
              v-model.number="form.year_built"
              label="Год постройки"
              icon="solar:calendar-linear"
              type="number"
              :error="fieldErrors.year_built"
            />
          </div>
          <label class="check-field">
            <input v-model="form.is_new_building" type="checkbox" />
            <span>Новостройка</span>
          </label>
        </div>

        <div class="form__section">
          <h3>Координаты</h3>
          <div class="form__grid">
            <BaseField
              v-model.number="form.latitude"
              label="Широта"
              icon="solar:map-point-linear"
              type="number"
              step="0.000001"
              :error="fieldErrors.latitude"
            />
            <BaseField
              v-model.number="form.longitude"
              label="Долгота"
              icon="solar:map-point-linear"
              type="number"
              step="0.000001"
              :error="fieldErrors.longitude"
            />
          </div>
          <p class="text-muted">Координаты нужны для отображения на карте.</p>
        </div>

        <div class="form__section">
          <h3>Фотографии</h3>
          <label class="upload-field" :class="{ 'upload-field--error': fieldErrors.image_files }">
            <input ref="fileInput" type="file" accept="image/*" multiple @change="handleImageFiles" />
            <span>Выбрать фотографии с компьютера</span>
            <small>Можно выбрать сразу несколько изображений.</small>
          </label>
          <small v-if="fieldErrors.image_files" class="field-error">{{ fieldErrors.image_files }}</small>
          <ul v-if="form.image_files.length" class="image-list">
            <li v-for="(file, idx) in form.image_files" :key="`${file.name}-${idx}`">
              <span>{{ file.name }}</span>
              <button type="button" class="link danger" @click="removeImageFile(idx)">Удалить</button>
            </li>
          </ul>
        </div>
        <BaseButton :disabled="saving" icon="solar:save-linear" type="submit" block>
          {{ saving ? "Сохраняем..." : editingId ? "Сохранить изменения" : "Сохранить объект" }}
        </BaseButton>
        <BaseButton v-if="editingId" type="button" variant="secondary" icon="solar:close-circle-linear" block @click="cancelEdit">
          Отменить редактирование
        </BaseButton>
      </form>
      <div v-else class="admin__notice">
        <h2>Недостаточно прав</h2>
        <p class="text-muted">Панель доступна только агенту или администратору сайта.</p>
      </div>

      <div class="admin__list">
        <h2>{{ listTitle }} ({{ properties.length }})</h2>
        <div class="admin__list-content">
          <article v-for="item in properties" :key="item.id" class="manage-item">
            <ListingCard :property="item" />
            <div class="manage-item__actions">
              <button type="button" class="manage-action manage-action--edit" @click="startEdit(item)">
                Редактировать
              </button>
              <button type="button" class="manage-action manage-action--delete" @click="deleteProperty(item)">
                Удалить
              </button>
            </div>
          </article>
          <p v-if="!properties.length" class="text-muted">Объектов пока нет.</p>
        </div>
      </div>

      <section v-if="isAdmin" class="agents-panel">
        <div class="agents-panel__header">
          <div>
            <h2>Агенты</h2>
            <p class="text-muted">Создайте аккаунт агента и передайте ему email и пароль для входа.</p>
          </div>
        </div>
        <form class="agent-form" @submit.prevent="createAgent">
          <p v-if="agentError" class="form__error">{{ agentError }}</p>
          <p v-if="agentSuccess" class="form__success">{{ agentSuccess }}</p>
          <div class="form__grid">
            <BaseField v-model="agentForm.email" label="Email агента" icon="solar:letter-linear" type="email" required />
            <BaseField v-model="agentForm.password" label="Пароль" icon="solar:lock-password-linear" type="password" required />
            <BaseField v-model="agentForm.first_name" label="Имя" icon="solar:user-linear" />
            <BaseField v-model="agentForm.last_name" label="Фамилия" icon="solar:user-id-linear" />
            <BaseField v-model="agentForm.phone" label="Телефон" icon="solar:phone-linear" />
          </div>
          <BaseButton :disabled="agentSaving" icon="solar:user-plus-linear" type="submit">
            {{ agentSaving ? "Создаём..." : "Создать агента" }}
          </BaseButton>
        </form>
        <div class="agents-list">
          <article v-for="agent in agents" :key="agent.id" class="agent-card">
            <div>
              <strong>{{ agentName(agent) }}</strong>
            
              <span>{{ agent.email }}</span>
            </div>
            <small>{{ agent.phone || "Телефон не указан" }}</small>
          </article>
          <p v-if="!agents.length" class="text-muted">Агенты пока не созданы.</p>
        </div>
      </section>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseChip from "@/components/ui/BaseChip.vue";
import BaseField from "@/components/ui/BaseField.vue";
import ListingCard from "@/components/ListingCard.vue";
import { useAuthStore } from "@/store/auth";
import api from "@/services/api";

const auth = useAuthStore();
const isAdmin = computed(() => auth.isAdmin);
const isAgent = computed(() => auth.isAgent);
const canManage = computed(() => auth.isAuthenticated && (isAdmin.value || isAgent.value));
const isAgentOnly = computed(() => auth.isAgent && !auth.isAdmin);
const panelBadge = computed(() => (isAdmin.value ? "Админ панель" : "Панель агента"));
const panelTitle = computed(() => (isAdmin.value ? "Управление сайтом" : "Мои объекты"));
const panelDescription = computed(() =>
  isAdmin.value
    ? "Управляйте недвижимостью и создавайте аккаунты агентов."
    : "Создавайте новые объекты, редактируйте свои объявления и держите витрину актуальной."
);
const listTitle = computed(() => (isAgentOnly.value ? "Мои объекты" : "Объекты"));
const properties = ref([]);
const agents = ref([]);
const fileInput = ref(null);
const formError = ref("");
const successMessage = ref("");
const fieldErrors = ref({});
const saving = ref(false);
const editingId = ref(null);
const agentError = ref("");
const agentSuccess = ref("");
const agentSaving = ref(false);
const form = reactive({
  title: "",
  description: "",
  price: null,
  area_total: null,
  living_area: null,
  kitchen_area: null,
  rooms: null,
  floor: null,
  floors_total: null,
  year_built: null,
  property_type: "apartment",
  address: "",
  district: "",
  city: "Санкт-Петербург",
  latitude: null,
  longitude: null,
  is_new_building: false,
  image_files: [],
});
const agentForm = reactive({
  email: "",
  password: "",
  first_name: "",
  last_name: "",
  phone: "",
});

const fetchProperties = async () => {
  try {
    const params = { page_size: 60 };
    if (isAgentOnly.value) {
      params.mine = "1";
    }
    const { data } = await api.get("/properties/", { params });
    properties.value = Array.isArray(data) ? data : data.results || [];
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error("fetch properties error", error?.response?.data || error);
    }
  }
};

const fetchAgents = async () => {
  if (!auth.isAdmin) return;
  try {
    const { data } = await api.get("/auth/admin/agents/");
    agents.value = Array.isArray(data) ? data : data.results || [];
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error("fetch agents error", error?.response?.data || error);
    }
  }
};

const handleImageFiles = (event) => {
  const files = Array.from(event.target.files || []);
  form.image_files = files;
};

const removeImageFile = (index) => {
  form.image_files.splice(index, 1);
  if (!form.image_files.length && fileInput.value) {
    fileInput.value.value = "";
  }
};

const resetForm = () => {
  Object.assign(form, {
    title: "",
    description: "",
    price: null,
    area_total: null,
    living_area: null,
    kitchen_area: null,
    rooms: null,
    floor: null,
    floors_total: null,
    year_built: null,
    property_type: "apartment",
    address: "",
    district: "",
    city: "Санкт-Петербург",
    latitude: null,
    longitude: null,
    is_new_building: false,
    image_files: [],
  });
  if (fileInput.value) {
    fileInput.value.value = "";
  }
  editingId.value = null;
};

const fieldLabel = (key) => {
  const mapping = {
    title: "Название",
    price: "Цена",
    city: "Город",
    address: "Адрес",
    district: "Район",
    property_type: "Тип объекта",
    rooms: "Комнаты",
    area_total: "Площадь",
    living_area: "Жилая площадь",
    kitchen_area: "Кухня",
    floor: "Этаж",
    floors_total: "Этажей в доме",
    year_built: "Год постройки",
    latitude: "Широта",
    longitude: "Долгота",
    image_files: "Фотографии",
  };
  return mapping[key] || key;
};

const normalizeText = (value) => {
  if (value === null || value === undefined) return null;
  const trimmed = String(value).trim();
  return trimmed ? trimmed : null;
};

const normalizeNumber = (value) => {
  if (value === null || value === undefined || value === "") return null;
  const num = Number(value);
  return Number.isFinite(num) ? num : null;
};

const buildPayload = () => {
  const payload = {
    title: normalizeText(form.title),
    description: normalizeText(form.description),
    price: normalizeNumber(form.price),
    property_type: form.property_type,
    city: normalizeText(form.city),
    district: normalizeText(form.district),
    address: normalizeText(form.address),
    rooms: normalizeNumber(form.rooms),
    area_total: normalizeNumber(form.area_total),
    living_area: normalizeNumber(form.living_area),
    kitchen_area: normalizeNumber(form.kitchen_area),
    floor: normalizeNumber(form.floor),
    floors_total: normalizeNumber(form.floors_total),
    year_built: normalizeNumber(form.year_built),
    is_new_building: Boolean(form.is_new_building),
    latitude: normalizeNumber(form.latitude),
    longitude: normalizeNumber(form.longitude),
  };
  Object.keys(payload).forEach((key) => {
    if (payload[key] === null || payload[key] === "") delete payload[key];
  });
  return payload;
};

const buildRequestBody = (payload) => {
  if (!form.image_files.length) {
    return payload;
  }
  const formData = new FormData();
  Object.entries(payload).forEach(([key, value]) => {
    formData.append(key, value);
  });
  form.image_files.forEach((file) => {
    formData.append("image_files", file);
  });
  return formData;
};

const startEdit = (property) => {
  editingId.value = property.id;
  formError.value = "";
  successMessage.value = "";
  fieldErrors.value = {};
  Object.assign(form, {
    title: property.title || "",
    description: property.description || "",
    price: property.price ?? null,
    area_total: property.area_total ?? null,
    living_area: property.living_area ?? null,
    kitchen_area: property.kitchen_area ?? null,
    rooms: property.rooms ?? null,
    floor: property.floor ?? null,
    floors_total: property.floors_total ?? null,
    year_built: property.year_built ?? null,
    property_type: property.property_type || "apartment",
    address: property.address || "",
    district: property.district || "",
    city: property.city || "",
    latitude: property.latitude ?? null,
    longitude: property.longitude ?? null,
    is_new_building: Boolean(property.is_new_building),
    image_files: [],
  });
  if (fileInput.value) {
    fileInput.value.value = "";
  }
  window.scrollTo({ top: 0, behavior: "smooth" });
};

const cancelEdit = () => {
  resetForm();
  successMessage.value = "";
  formError.value = "";
  fieldErrors.value = {};
};

const parseErrors = (error) => {
  const data = error?.response?.data;
  if (!data) return { message: "Не удалось сохранить объект.", fields: {} };
  if (data.detail) return { message: data.detail, fields: {} };
  if (typeof data === "object") {
    if (Array.isArray(data.non_field_errors) && data.non_field_errors.length) {
      return { message: data.non_field_errors[0], fields: {} };
    }
    const fields = {};
    Object.entries(data).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        fields[key] = value[0];
      } else if (typeof value === "string") {
        fields[key] = value;
      } else if (value && typeof value === "object") {
        const nested = Object.values(value)[0];
        if (Array.isArray(nested)) {
          fields[key] = nested[0];
        }
      }
    });
    return { message: "Проверьте поля формы.", fields };
  }
  return { message: "Не удалось сохранить объект.", fields: {} };
};

const resetAgentForm = () => {
  Object.assign(agentForm, {
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    phone: "",
  });
};

const agentName = (agent) => {
  return [agent.first_name, agent.last_name].filter(Boolean).join(" ") || "Агент";
};

const createAgent = async () => {
  agentError.value = "";
  agentSuccess.value = "";
  const payload = {
    email: normalizeText(agentForm.email),
    password: normalizeText(agentForm.password),
    first_name: normalizeText(agentForm.first_name),
    last_name: normalizeText(agentForm.last_name),
    phone: normalizeText(agentForm.phone),
  };
  Object.keys(payload).forEach((key) => {
    if (payload[key] === null || payload[key] === "") delete payload[key];
  });
  if (!payload.email || !payload.password) {
    agentError.value = "Укажите email и пароль агента.";
    return;
  }
  try {
    agentSaving.value = true;
    const { data } = await api.post("/auth/admin/agents/", payload);
    agents.value = [data, ...agents.value.filter((agent) => agent.id !== data.id)];
    resetAgentForm();
    agentSuccess.value = "Агент создан. Передайте ему email и пароль для входа.";
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error("create agent error", error?.response?.data || error);
    }
    agentError.value = parseErrors(error).message;
  } finally {
    agentSaving.value = false;
  }
};

const saveProperty = async () => {
  formError.value = "";
  successMessage.value = "";
  fieldErrors.value = {};
  const payload = buildPayload();
  if (!payload.title || payload.price === undefined || !payload.city || !payload.address) {
    formError.value = "Заполните обязательные поля: название, цена, город и адрес.";
    return;
  }
  try {
    saving.value = true;
    const wasEditing = Boolean(editingId.value);
    const requestBody = buildRequestBody(payload);
    const { data } = editingId.value
      ? await api.patch(`/properties/${editingId.value}/`, requestBody)
      : await api.post("/properties/", requestBody);
    if (data?.id) {
      properties.value = [data, ...properties.value.filter((item) => item.id !== data.id)];
      window.dispatchEvent(new CustomEvent("listing:created", { detail: data }));
    }
    resetForm();
    await fetchProperties();
    successMessage.value = wasEditing ? "Объект обновлён." : "Объект добавлен.";
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error("save property error", error?.response?.data || error);
    }
    const parsed = parseErrors(error);
    formError.value = parsed.message;
    fieldErrors.value = parsed.fields;
  } finally {
    saving.value = false;
  }
};

const deleteProperty = async (property) => {
  const confirmed = window.confirm(`Удалить объект “${property.title || "Без названия"}”?`);
  if (!confirmed) return;
  try {
    await api.delete(`/properties/${property.id}/`);
    properties.value = properties.value.filter((item) => item.id !== property.id);
    if (editingId.value === property.id) {
      resetForm();
    }
    successMessage.value = "Объект удалён.";
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error("delete property error", error?.response?.data || error);
    }
    formError.value = "Не удалось удалить объект.";
  }
};

const syncCian = async () => {
  await api.post("/properties/sync/");
  fetchProperties();
};

const geocode = async () => {
  await api.post("/properties/geocode/");
  fetchProperties();
};

onMounted(async () => {
  await auth.fetchCurrentUser();
  fetchProperties();
  fetchAgents();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;
@use "@/styles/mixins" as *;

.admin {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.admin__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;

  h1 {
    @include heading-xl;
  }

  @include mobile {
    flex-direction: column;
    align-items: flex-start;
  }
}

.admin__actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.admin__grid {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
  gap: 1.5rem;
  align-items: stretch;

  @include mobile {
    grid-template-columns: 1fr;
  }
}

.form {
  @include card;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;

  @include mobile {
    padding: 1.25rem;
  }
}

.form__section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form__error {
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #b91c1c;
  padding: 0.75rem 1rem;
  border-radius: $radius-md;
}

.form__success {
  background: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.2);
  color: #166534;
  padding: 0.75rem 1rem;
  border-radius: $radius-md;
}

.form__edit-note {
  margin: 0;
  border-radius: $radius-md;
  background: rgba(31, 117, 255, 0.08);
  color: $color-primary;
  padding: 0.75rem 1rem;
  font-weight: 600;
  line-height: 1.45;
}

.form__errors {
  margin: 0;
  padding: 0.75rem 1rem;
  list-style: none;
  border-radius: $radius-md;
  background: rgba(15, 23, 42, 0.05);
  color: $color-muted;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form__grid {
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
  gap: 0.4rem;

  select {
    padding: 0.75rem 1rem;
    border-radius: $radius-md;
    border: 1px solid rgba(15, 23, 42, 0.1);
  }
}

.image-list {
  background: rgba(15, 23, 42, 0.03);
  padding: 1rem;
  border-radius: $radius-md;
  color: $color-muted;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;

  li {
    display: flex;
    justify-content: space-between;
    gap: 0.75rem;
    align-items: center;
  }
}

.upload-field {
  border: 1px dashed rgba(31, 117, 255, 0.35);
  border-radius: $radius-md;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  cursor: pointer;
  background: rgba(31, 117, 255, 0.05);
  transition: border-color $transition-base, background $transition-base;

  &:hover {
    border-color: $color-primary;
    background: rgba(31, 117, 255, 0.09);
  }

  input {
    position: absolute;
    width: 1px;
    height: 1px;
    opacity: 0;
    pointer-events: none;
  }

  span {
    color: $color-primary;
    font-weight: 700;
  }

  small {
    color: $color-muted;
  }
}

.upload-field--error {
  border-color: rgba(239, 68, 68, 0.55);
  background: rgba(239, 68, 68, 0.08);
}

.field-error {
  color: #b91c1c;
  font-size: 0.85rem;
}

.check-field {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  input {
    width: 18px;
    height: 18px;
  }
}

.link {
  background: none;
  border: none;
  color: $color-primary;
  cursor: pointer;
  font-weight: 600;
}

.link.danger {
  color: #ef4444;
}

.admin__notice {
  @include card;
  padding: 1.5rem;
}

.admin__list {
  @include card;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  min-height: 0;
  height: 100%;

  @include mobile {
    padding: 1.25rem;
    height: auto;
  }
}

.admin__list-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  flex: 1;
  min-height: 0;
  height: 100%;
  overflow-y: auto;
  padding-right: 0.5rem;

  @include mobile {
    height: auto;
    overflow: visible;
  }
}

.manage-item {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.manage-item__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  flex-wrap: wrap;
  padding: 0 0.25rem;

  @include mobile {
    justify-content: stretch;

    .manage-action {
      flex: 1;
    }
  }
}

.manage-action {
  min-height: 42px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: $radius-md;
  padding: 0.65rem 1rem;
  font-weight: 800;
  cursor: pointer;
  background: rgba(15, 23, 42, 0.04);
  color: $color-primary;
  transition: transform $transition-base, box-shadow $transition-base, background $transition-base;

  &:hover {
    transform: translateY(-1px);
    box-shadow: $shadow-soft;
    background: #fff;
  }
}

.manage-action--delete {
  color: #dc2626;
  background: rgba(239, 68, 68, 0.08);
  border-color: rgba(239, 68, 68, 0.18);
}

.agents-panel {
  @include card;
  grid-column: 1 / -1;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;

  @include mobile {
    padding: 1.25rem;
  }
}

.agents-panel__header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.agent-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.agents-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.75rem;

  @include mobile {
    grid-template-columns: 1fr;
  }
}

.agent-card {
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: $radius-md;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  background: rgba(255, 255, 255, 0.75);

  div {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    min-width: 0;
  }

  span,
  small {
    color: $color-muted;
    word-break: break-word;
  }

  @include mobile {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
