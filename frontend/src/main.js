import { createApp } from "vue";
import { createPinia } from "pinia";
import FloatingVue from "floating-vue";
import "floating-vue/dist/style.css";
import { MotionPlugin } from "@vueuse/motion";
import App from "./App.vue";
import router from "./router";
import "./styles/main.scss";

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.use(FloatingVue, { themes: { tooltip: { delay: { show: 300, hide: 0 } } } });
app.use(MotionPlugin);
app.mount("#app");
