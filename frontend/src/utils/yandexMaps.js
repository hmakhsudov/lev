let loaderPromise = null;

export const loadYandexMaps = () => {
  if (window.ymaps) return Promise.resolve(window.ymaps);
  if (loaderPromise) return loaderPromise;

  const apiKey = import.meta.env.VITE_YANDEX_MAPS_API_KEY || "";
  const script = document.createElement("script");
  script.src = `https://api-maps.yandex.ru/2.1/?apikey=${apiKey}&lang=ru_RU`;
  script.async = true;

  loaderPromise = new Promise((resolve, reject) => {
    script.onload = () => {
      if (!window.ymaps) {
        reject(new Error("Не удалось инициализировать Яндекс.Карты."));
        return;
      }
      window.ymaps.ready(() => resolve(window.ymaps));
    };
    script.onerror = () => reject(new Error("Не удалось загрузить Яндекс.Карты."));
  });

  document.head.appendChild(script);
  return loaderPromise;
};
