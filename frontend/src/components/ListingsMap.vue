<template>
  <div class="map" ref="mapRef">
    <div v-if="loading" class="map__loading">
      <SkeletonBlock height="320px" />
      <p>Загружаем карту...</p>
    </div>
    <div v-else-if="!hasCoordinates" class="map__empty">
      <Icon icon="solar:map-point-outline" width="28" />
      <p>Для этих объектов нет координат</p>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { Icon } from "@iconify/vue";
import SkeletonBlock from "@/components/ui/SkeletonBlock.vue";

const props = defineProps({
  properties: { type: Array, default: () => [] },
  selectedPropertyId: { type: [Number, String], default: null },
});

const mapRef = ref(null);
let mapInstance = null;
let markers = [];
const markersMap = new Map();
let scriptPromise;
const loading = ref(true);
const DEFAULT_CENTER = [59.9386, 30.3141];

const hasCoordinates = computed(() =>
  props.properties.some((item) => hasPoint(item))
);

const createMarkerContent = (item) => {
  const price = formatPrice(item.price);
  const meta = [];
  const rooms = item.rooms ? `${item.rooms}-к` : "";
  if (rooms) meta.push(rooms);
  const area = formatArea(item.area_total);
  if (area) meta.push(area);
  const subtitle = meta.length ? meta.join(" · ") : item.city || "";
  return `<div class="map-marker">
      <span class="map-marker__price">${price}</span>
      <small>${subtitle}</small>
    </div>`;
};

const loadYMaps = () => {
  if (window.ymaps) return Promise.resolve(window.ymaps);
  if (scriptPromise) return scriptPromise;
  const apiKey = import.meta.env.VITE_YANDEX_MAPS_API_KEY || "";
  const script = document.createElement("script");
  script.src = `https://api-maps.yandex.ru/2.1/?apikey=${apiKey}&lang=ru_RU`;
  script.async = true;
  scriptPromise = new Promise((resolve, reject) => {
    script.onload = () => window.ymaps.ready(() => resolve(window.ymaps));
    script.onerror = () => reject(new Error("Не удалось загрузить карту"));
  });
  document.head.appendChild(script);
  return scriptPromise;
};

const renderMarkers = () => {
  if (!mapInstance || !window.ymaps) return;
  markers.forEach((marker) => mapInstance.geoObjects.remove(marker));
  markers = [];
  markersMap.clear();
  const coords = [];
  props.properties
    .filter((item) => hasPoint(item))
    .forEach((item) => {
      const point = [Number(item.latitude), Number(item.longitude)];
      coords.push(point);
      const placemark = new window.ymaps.Placemark(
        point,
        {
          balloonContent: `<div class="map-balloon">
              <strong>${item.title || "Объект"}</strong>
              <div class="map-balloon__price">${formatPrice(item.price)}</div>
              <p>${item.address || ""}</p>
              <a href="/property/${item.id}" target="_blank">Подробнее</a>
            </div>`,
          hintContent: item.title || "Объект",
        },
        {
          iconLayout: "default#imageWithContent",
          iconImageHref: "",
          iconImageSize: [0, 0],
          iconImageOffset: [0, 0],
          iconContentLayout: window.ymaps.templateLayoutFactory.createClass(createMarkerContent(item)),
        }
      );
      placemark.events.add("mouseenter", () => placemark.balloon.open());
      placemark.events.add("mouseleave", () => placemark.balloon.close());
      placemark.events.add("click", () => {
        placemark.balloon.isOpen()
          ? placemark.balloon.close()
          : placemark.balloon.open();
      });
      mapInstance.geoObjects.add(placemark);
      markers.push(placemark);
      markersMap.set(String(item.id), placemark);
    });
  if (coords.length === 1) {
    mapInstance.setCenter(coords[0], 13);
  } else if (coords.length > 1) {
    const lats = coords.map((point) => point[0]);
    const lngs = coords.map((point) => point[1]);
    const bounds = [
      [Math.min(...lats), Math.min(...lngs)],
      [Math.max(...lats), Math.max(...lngs)],
    ];
    mapInstance.setBounds(bounds, { checkZoomRange: true, zoomMargin: 40 });
  } else {
    mapInstance.setCenter(DEFAULT_CENTER, 11);
  }
  updateMarkerScale(mapInstance?.getZoom());
  if (props.selectedPropertyId) {
    focusOnMarker(String(props.selectedPropertyId));
  }
};

onMounted(async () => {
  try {
    const ymaps = await loadYMaps();
    mapInstance = new ymaps.Map(
      mapRef.value,
      {
        center: DEFAULT_CENTER,
        zoom: 11,
        controls: ["zoomControl"],
      },
      {
        suppressMapOpenBlock: true,
        yandexMapDisablePoiInteractivity: true,
      }
    );
    updateMarkerScale(mapInstance.getZoom());
    loading.value = false;
    renderMarkers();
  } catch (error) {
    loading.value = false;
    console.warn(error.message);
  }
});

watch(
  () => props.properties,
  () => {
    renderMarkers();
  },
  { deep: true }
);

watch(
  () => props.selectedPropertyId,
  (id) => {
    if (!id) return;
    focusOnMarker(String(id));
  }
);

onBeforeUnmount(() => {
  markers = [];
  mapInstance = null;
});

const hasPoint = (item) => item && item.latitude && item.longitude;

const formatPrice = (value) => {
  if (value === null || value === undefined) return "—";
  const number = Number(value);
  if (Number.isNaN(number)) return "—";
  return `${new Intl.NumberFormat("ru-RU").format(number)} ₽`;
};

const formatArea = (value) => {
  if (value === null || value === undefined) return "";
  const number = Number(value);
  if (Number.isNaN(number)) return "";
  return `${number.toLocaleString("ru-RU")} м²`;
};

const focusOnMarker = (id) => {
  if (!mapInstance || !window.ymaps) return;
  const marker = markersMap.get(id);
  if (!marker) return;
  const coords = marker.geometry.getCoordinates();
  mapInstance.setCenter(coords, 14, { duration: 300 });
  marker.balloon.open();
};

const updateMarkerScale = (zoom = 11) => {
  if (!mapRef.value) return;
  const scale = Math.max(0.65, Math.min(1.05, 1 - (zoom - 11) * 0.06));
  mapRef.value.style.setProperty("--marker-scale", `${scale}`);
};
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;

.map {
  width: 100%;
  height: 100%;
  min-height: 320px;
  border-radius: $radius-lg;
  overflow: hidden;
  position: relative;
  box-shadow: $shadow-card;
}

.map__loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.8);
}

:global(.map-marker) {
  padding: 0.3rem 0.75rem;
  border-radius: $radius-md;
  background: linear-gradient(135deg, $color-primary, #6b8cff);
  color: #fff;
  font-weight: 600;
  box-shadow: $shadow-soft;
  display: inline-flex;
  flex-direction: column;
  text-align: center;
  min-width: 90px;
  transform: scale(var(--marker-scale, 1));
  transition: transform 0.2s ease;

  .map-marker__price {
    font-weight: 700;
  }

  small {
    font-weight: 500;
    color: rgba(255, 255, 255, 0.85);
    font-size: 0.75rem;
  }
}

.map__empty {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  align-items: center;
  justify-content: center;
  color: $color-muted;
  background: rgba(255, 255, 255, 0.95);
}

:global(.map-balloon) {
  font-size: 0.85rem;
  min-width: 140px;

  .map-balloon__price {
    font-weight: 600;
    margin: 0.2rem 0 0.4rem;
  }

  a {
    color: $color-primary;
    font-weight: 600;
  }
}
</style>
