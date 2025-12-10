import { createRouter, createWebHistory } from "vue-router";

import HomePage from "@/pages/HomePage.vue";
import PropertyDetailPage from "@/pages/PropertyDetailPage.vue";
import AssistantPage from "@/pages/AssistantPage.vue";
import AdminDashboard from "@/pages/AdminDashboard.vue";
import LoginPage from "@/pages/LoginPage.vue";
import RegisterPage from "@/pages/RegisterPage.vue";

const routes = [
  { path: "/", component: HomePage },
  { path: "/property/:id", component: PropertyDetailPage, props: true },
  { path: "/assistant", component: AssistantPage },
  { path: "/admin", component: AdminDashboard },
  { path: "/login", component: LoginPage },
  { path: "/register", component: RegisterPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
