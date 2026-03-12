<template>
  <div class="re-map" ref="mapRef">
    <div v-if="loading" class="re-map__state">
      <SkeletonBlock height="320px" />
      <p>Загружаем карту...</p>
    </div>
    <div v-else-if="errorMessage" class="re-map__state re-map__state--error">
      <Icon icon="solar:danger-circle-outline" width="26" />
      <p>{{ errorMessage }}</p>
    </div>
    <div v-else-if="!validListings.length" class="re-map__state">
      <Icon icon="solar:map-point-outline" width="28" />
      <p>Для этих объектов нет координат</p>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { Icon } from "@iconify/vue";
import SkeletonBlock from "@/components/ui/SkeletonBlock.vue";
import { loadYandexMaps } from "@/utils/yandexMaps";

const props = defineProps({
  listings: { type: Array, default: () => [] },
  selectedId: { type: [Number, String], default: null },
});

const emit = defineEmits(["marker-click", "bounds-change"]);

const mapRef = ref(null);
const loading = ref(true);
const errorMessage = ref("");

let mapInstance = null;
let clusterer = null;
let placemarksById = new Map();
let ymapsApi = null;
let bubbleLayout = null;
let bubbleLayoutSelected = null;
let clusterLayout = null;

const DEFAULT_CENTER = [59.9386, 30.3141];

const validListings = computed(() =>
  props.listings.filter((item) => hasValidCoords(item))
);

const hasValidCoords = (item) => {
  const lat = Number(item?.latitude);
  const lng = Number(item?.longitude);
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return false;
  if (lat === 0 || lng === 0) return false;
  return true;
};

const formatPrice = (value) => {
  if (value === null || value === undefined) return "—";
  const number = Number(value);
  if (!Number.isFinite(number)) return "—";
  return `${new Intl.NumberFormat("ru-RU").format(number)} ₽`;
};

const formatArea = (value) => {
  if (value === null || value === undefined) return "";
  const number = Number(value);
  if (!Number.isFinite(number)) return "";
  return `${number.toLocaleString("ru-RU")} м²`;
};

const createLayouts = () => {
  bubbleLayout = ymapsApi.templateLayoutFactory.createClass(
    '<div class="re-map__bubble"><span>$[properties.iconContent]</span></div>'
  );
  bubbleLayoutSelected = ymapsApi.templateLayoutFactory.createClass(
    '<div class="re-map__bubble re-map__bubble--selected"><span>$[properties.iconContent]</span></div>'
  );
  clusterLayout = ymapsApi.templateLayoutFactory.createClass(
    '<div class="re-map__cluster">$[properties.geoObjects.length]</div>'
  );
};

const buildBalloonContent = (item) => {
  const img = item.main_image || item.images?.[0];
  const title = item.title || "Объект недвижимости";
  const address = item.address || "";
  const meta = [formatRooms(item.rooms), formatArea(item.area_total)].filter(Boolean).join(" · ");
  return `<div class="re-map__balloon">
      ${img ? `<img src="${img}" alt="${title}" />` : ""}
      <div class="re-map__balloon-body">
        <strong>${title}</strong>
        ${meta ? `<div class="re-map__balloon-meta">${meta}</div>` : ""}
        <div class="re-map__balloon-price">${formatPrice(item.price)}</div>
        <div class="re-map__balloon-address">${address}</div>
        <a class="re-map__balloon-link" href="/property/${item.id}">Подробнее</a>
      </div>
    </div>`;
};

const formatRooms = (rooms) => {
  if (!rooms) return "";
  return `${rooms}-к`;
};

const buildPlacemark = (item) => {
  const coords = [Number(item.latitude), Number(item.longitude)];
  const hint = [formatPrice(item.price), formatRooms(item.rooms), formatArea(item.area_total)]
    .filter(Boolean)
    .join(" · ");
  const placemark = new ymapsApi.Placemark(
    coords,
    {
      iconContent: formatPrice(item.price),
      hintContent: hint || "Объект недвижимости",
      balloonContent: buildBalloonContent(item),
    },
    {
      iconLayout: "default#imageWithContent",
      iconImageHref: "",
      iconImageSize: [0, 0],
      iconImageOffset: [0, 0],
      iconContentLayout: bubbleLayout,
      hideIconOnBalloonOpen: false,
      openBalloonOnClick: true,
      balloonShadow: true,
      balloonOffset: [0, -20],
      balloonCloseButton: true,
      iconShape: {
        type: "Rectangle",
        coordinates: [
          [-40, -22],
          [40, 22],
        ],
      },
    }
  );

  placemark.events.add("click", () => {
    emit("marker-click", item);
  });
  placemark.events.add("mouseenter", () => {
    if (!placemark.balloon.isOpen()) {
      placemark.balloon.open();
    }
  });
  placemark.events.add("mouseleave", () => {
    if (String(props.selectedId) === String(item.id)) return;
    placemark.balloon.close();
  });

  return placemark;
};

const clearMap = () => {
  if (!mapInstance) return;
  mapInstance.geoObjects.removeAll();
  placemarksById = new Map();
  clusterer = null;
};

const renderMarkers = () => {
  if (!mapInstance || !ymapsApi) return;
  clearMap();

  const items = validListings.value;
  if (!items.length) {
    mapInstance.setCenter(DEFAULT_CENTER, 11);
    return;
  }

  clusterer = new ymapsApi.Clusterer({
    clusterDisableClickZoom: false,
    clusterOpenBalloonOnClick: true,
    clusterBalloonPanelMaxMapArea: 0,
    clusterBalloonContentLayout: "cluster#balloonCarousel",
    clusterBalloonItemContentLayout: "cluster#balloonItem",
    clusterBalloonPagerSize: 5,
    clusterIconLayout: "default#imageWithContent",
    clusterIconContentLayout: clusterLayout,
    clusterIconImageHref: "",
    clusterIconImageSize: [0, 0],
    clusterIconImageOffset: [0, 0],
    clusterIconShape: {
      type: "Rectangle",
      coordinates: [
        [-22, -22],
        [22, 22],
      ],
    },
  });

  const placemarks = items.map((item) => {
    const placemark = buildPlacemark(item);
    placemarksById.set(String(item.id), placemark);
    return placemark;
  });

  clusterer.add(placemarks);
  mapInstance.geoObjects.add(clusterer);

  const coords = items.map((item) => [Number(item.latitude), Number(item.longitude)]);
  if (coords.length === 1) {
    mapInstance.setCenter(coords[0], 13);
  } else {
    const lats = coords.map((point) => point[0]);
    const lngs = coords.map((point) => point[1]);
    const bounds = [
      [Math.min(...lats), Math.min(...lngs)],
      [Math.max(...lats), Math.max(...lngs)],
    ];
    mapInstance.setBounds(bounds, { checkZoomRange: true, zoomMargin: 48 });
  }

  if (props.selectedId) {
    highlightMarker(String(props.selectedId));
  }
};

const highlightMarker = (id) => {
  if (!mapInstance || !placemarksById.size) return;
  placemarksById.forEach((placemark, key) => {
    placemark.options.set(
      "iconContentLayout",
      key === id ? bubbleLayoutSelected : bubbleLayout
    );
  });
  const selected = placemarksById.get(id);
  if (!selected) return;
  const coords = selected.geometry.getCoordinates();
  mapInstance.setCenter(coords, Math.max(mapInstance.getZoom(), 13), { duration: 300 });
  selected.balloon.open();
};

const handleBoundsChange = () => {
  if (!mapInstance) return;
  const bounds = mapInstance.getBounds();
  emit("bounds-change", bounds);
};

onMounted(async () => {
  loading.value = true;
  try {
    ymapsApi = await loadYandexMaps();
    createLayouts();
    mapInstance = new ymapsApi.Map(
      mapRef.value,
      {
        center: DEFAULT_CENTER,
        zoom: 11,
        controls: ["zoomControl"],
      },
      { suppressMapOpenBlock: true }
    );
    mapInstance.events.add("boundschange", handleBoundsChange);
    renderMarkers();
  } catch (error) {
    errorMessage.value = error.message || "Не удалось загрузить карту.";
  } finally {
    loading.value = false;
  }
});

watch(
  () => props.listings,
  () => {
    renderMarkers();
  },
  { deep: true }
);

watch(
  () => props.selectedId,
  (value) => {
    if (value === null || value === undefined) return;
    highlightMarker(String(value));
  }
);

onBeforeUnmount(() => {
  if (mapInstance) {
    mapInstance.events.remove("boundschange", handleBoundsChange);
    mapInstance.destroy();
  }
  mapInstance = null;
  placemarksById = new Map();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;

.re-map {
  width: 100%;
  height: 100%;
  min-height: 320px;
  border-radius: $radius-lg;
  overflow: hidden;
  position: relative;
  box-shadow: $shadow-card;
}

.re-map__state {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  color: $color-muted;
}

.re-map__state--error {
  color: #b91c1c;
}

:global(.re-map__bubble) {
  padding: 0.35rem 0.9rem;
  border-radius: 999px;
  background: #ffffff;
  border: 2px solid rgba(31, 117, 255, 0.2);
  color: #0f172a;
  font-weight: 700;
  box-shadow: $shadow-soft;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 90px;
}

:global(.re-map__bubble--selected) {
  background: linear-gradient(135deg, $color-primary, #7c9bff);
  border-color: rgba(31, 117, 255, 0.5);
  color: #fff;
}

:global(.re-map__cluster) {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #0f172a;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  box-shadow: $shadow-soft;
}

:global(.re-map__balloon) {
  display: grid;
  grid-template-columns: 72px 1fr;
  gap: 0.75rem;
  min-width: 220px;
  font-size: 0.85rem;

  img {
    width: 72px;
    height: 72px;
    border-radius: 10px;
    object-fit: cover;
  }
}

:global(.re-map__balloon-body) {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

:global(.re-map__balloon-meta) {
  color: $color-muted;
  font-size: 0.78rem;
}

:global(.re-map__balloon-price) {
  font-weight: 700;
}

:global(.re-map__balloon-address) {
  color: $color-muted;
}

:global(.re-map__balloon-link) {
  color: $color-primary;
  font-weight: 600;
}
</style>
