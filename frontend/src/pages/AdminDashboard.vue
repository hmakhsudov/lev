<template>
  <div class="admin container">
    <header class="admin__header">
      <div>
        <BaseChip icon="solar:shield-check-bold">Панель агента</BaseChip>
        <h1>Управление объектами</h1>
        <p class="text-muted">Создавайте, редактируйте и синхронизируйте объекты напрямую с карты и AI.</p>
      </div>
      <div class="admin__actions">
        <!-- <BaseButton icon="solar:database-linear" variant="secondary" @click="syncCian">Синхронизировать CIAN</BaseButton>
        <BaseButton icon="solar:compass-linear" variant="ghost" @click="geocode">Геокодировать</BaseButton> -->
      </div>
    </header>

    <section class="admin__grid">
      <form v-if="canManage" class="form" @submit.prevent="saveProperty">
        <h2>Создать объект</h2>
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
              icon="solar:ruler-cross-linear"
              type="number"
              step="0.1"
              :error="fieldErrors.area_total"
            />
            <BaseField
              v-model.number="form.living_area"
              label="Площадь жилая"
              icon="solar:ruler-cross-linear"
              type="number"
              step="0.1"
              :error="fieldErrors.living_area"
            />
            <BaseField
              v-model.number="form.kitchen_area"
              label="Площадь кухни"
              icon="solar:ruler-cross-linear"
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

        <div class="images">
          <BaseField
            v-model="imageUrl"
            label="URL изображения"
            icon="solar:gallery-linear"
            placeholder="https://..."
            :error="fieldErrors.image_urls"
          />
          <BaseButton type="button" variant="secondary" icon="solar:add-circle-line-duotone" @click="addImage">Добавить</BaseButton>
        </div>
        <ul class="image-list">
          <li v-for="(img, idx) in form.image_urls" :key="img">
            <span>{{ img }}</span>
            <button type="button" class="link danger" @click="removeImage(idx)">Удалить</button>
          </li>
        </ul>
        <BaseButton :disabled="saving" icon="solar:save-linear" type="submit" block>
          {{ saving ? "Сохраняем..." : "Сохранить объект" }}
        </BaseButton>
      </form>
      <div v-else class="admin__notice">
        <h2>Недостаточно прав</h2>
        <p class="text-muted">Создавать и редактировать объекты могут только агент или администратор.</p>
      </div>

      <div class="admin__list">
        <h2>Мои объекты ({{ properties.length }})</h2>
        <div class="admin__list-content">
          <ListingCard v-for="item in properties" :key="item.id" :property="item" />
        </div>
      </div>
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
const canManage = computed(() => auth.isAuthenticated && (auth.isAdmin || auth.isAgent));
const properties = ref([]);
const imageUrl = ref("");
const formError = ref("");
const successMessage = ref("");
const fieldErrors = ref({});
const saving = ref(false);
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
  image_urls: [],
});

const fetchProperties = async () => {
  try {
    const { data } = await api.get("/properties/");
    properties.value = data;
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error("fetch properties error", error?.response?.data || error);
    }
  }
};

const addImage = () => {
  if (!imageUrl.value) return;
  form.image_urls.push(imageUrl.value);
  imageUrl.value = "";
};

const removeImage = (index) => {
  form.image_urls.splice(index, 1);
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
    image_urls: [],
  });
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
    image_urls: "Фотографии",
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
    image_urls: form.image_urls.length ? [...form.image_urls] : null,
  };
  Object.keys(payload).forEach((key) => {
    if (payload[key] === null || payload[key] === "") delete payload[key];
  });
  return payload;
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

const saveProperty = async () => {
  formError.value = "";
  successMessage.value = "";
  fieldErrors.value = {};
  const payload = buildPayload();
  if (!payload.title || !payload.price || !payload.city || !payload.address) {
    formError.value = "Заполните обязательные поля: название, цена, город и адрес.";
    return;
  }
  try {
    saving.value = true;
    const { data } = await api.post("/properties/", payload);
    if (data?.id) {
      properties.value = [data, ...properties.value.filter((item) => item.id !== data.id)];
      window.dispatchEvent(new CustomEvent("listing:created", { detail: data }));
    }
    resetForm();
    await fetchProperties();
    successMessage.value = "Объект добавлен.";
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

.images {
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;

  @include mobile {
    flex-direction: column;
    align-items: stretch;
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

  @include mobile {
    padding: 1.25rem;
  }
}

.admin__list-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 80vh;
  overflow-y: auto;
  padding-right: 0.5rem;

  @include mobile {
    max-height: none;
    overflow: visible;
  }
}
</style>
