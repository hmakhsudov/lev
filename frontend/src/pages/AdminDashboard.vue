<template>
  <div class="admin container">
    <header class="admin__header">
      <div>
        <BaseChip icon="solar:shield-check-bold">Панель агента</BaseChip>
        <h1>Управление объектами</h1>
        <p class="text-muted">Создавайте, редактируйте и синхронизируйте объекты напрямую с карты и AI.</p>
      </div>
      <div class="admin__actions">
        <BaseButton icon="solar:database-linear" variant="secondary" @click="syncCian">Синхронизировать CIAN</BaseButton>
        <BaseButton icon="solar:compass-linear" variant="ghost" @click="geocode">Геокодировать</BaseButton>
      </div>
    </header>

    <section class="admin__grid">
      <form class="form" @submit.prevent="saveProperty">
        <h2>Создать объект</h2>
        <div class="form__grid">
          <BaseField v-model="form.title" label="Название" icon="solar:home-add-linear" required />
          <BaseField v-model.number="form.price" label="Цена" icon="solar:wallet-linear" type="number" required />
          <BaseField v-model.number="form.area" label="Площадь" icon="solar:ruler-cross-linear" type="number" step="0.1" />
          <BaseField v-model.number="form.rooms" label="Комнат" icon="solar:bed-linear" type="number" min="1" />
          <BaseField v-model.number="form.floor" label="Этаж" icon="solar:buildings-2-linear" type="number" />
          <BaseField v-model.number="form.floors_total" label="Этажей в доме" icon="solar:buildings-linear" type="number" />
          <BaseField v-model="form.address" label="Адрес" icon="solar:map-point-line-duotone" />
          <BaseField v-model="form.district" label="Район" icon="solar:map-point-favourite-bold" />
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
        <BaseField v-model="form.description" label="Описание" icon="solar:document-text-linear" tag="textarea" rows="4" />
        <div class="images">
          <BaseField v-model="imageUrl" label="URL изображения" icon="solar:gallery-linear" placeholder="https://..." />
          <BaseButton type="button" variant="secondary" icon="solar:add-circle-line-duotone" @click="addImage">Добавить</BaseButton>
        </div>
        <ul class="image-list">
          <li v-for="(img, idx) in form.gallery" :key="idx">{{ img.url }}</li>
        </ul>
        <BaseButton icon="solar:save-linear" type="submit" block>Сохранить объект</BaseButton>
      </form>

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
import { onMounted, reactive, ref } from "vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseChip from "@/components/ui/BaseChip.vue";
import BaseField from "@/components/ui/BaseField.vue";
import ListingCard from "@/components/ListingCard.vue";
import { useAuthStore } from "@/store/auth";
import api from "@/services/api";

const auth = useAuthStore();
const properties = ref([]);
const imageUrl = ref("");
const form = reactive({
  title: "",
  description: "",
  price: null,
  area: null,
  rooms: 1,
  floor: 1,
  floors_total: 1,
  property_type: "apartment",
  address: "",
  district: "",
  city: "Санкт-Петербург",
  gallery: [],
});

const fetchProperties = async () => {
  const { data } = await api.get("/properties/");
  properties.value = data;
};

const addImage = () => {
  if (!imageUrl.value) return;
  form.gallery.push({ url: imageUrl.value });
  imageUrl.value = "";
};

const resetForm = () => {
  Object.assign(form, {
    title: "",
    description: "",
    price: null,
    area: null,
    rooms: 1,
    floor: 1,
    floors_total: 1,
    property_type: "apartment",
    address: "",
    district: "",
    city: "Санкт-Петербург",
    gallery: [],
  });
};

const saveProperty = async () => {
  await api.post("/properties/", form);
  resetForm();
  fetchProperties();
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

  @media (max-width: 960px) {
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

  @media (max-width: 1100px) {
    grid-template-columns: 1fr;
  }
}

.form {
  @include card;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
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
}

.image-list {
  background: rgba(15, 23, 42, 0.03);
  padding: 1rem;
  border-radius: $radius-md;
  color: $color-muted;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.admin__list {
  @include card;
  padding: 1.5rem;
}

.admin__list-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 80vh;
  overflow-y: auto;
  padding-right: 0.5rem;
}
</style>
