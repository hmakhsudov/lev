import { createRouter, createWebHistory } from "vue-router";

import HomePage from "@/pages/HomePage.vue";
import PropertyDetailPage from "@/pages/PropertyDetailPage.vue";
import AssistantPage from "@/pages/AssistantPage.vue";
import AdminDashboard from "@/pages/AdminDashboard.vue";
import LoginPage from "@/pages/LoginPage.vue";
import RegisterPage from "@/pages/RegisterPage.vue";
import CabinetPage from "@/pages/CabinetPage.vue";
import FavoritesPage from "@/pages/FavoritesPage.vue";
import DialogsPage from "@/pages/DialogsPage.vue";
import DialogDetailPage from "@/pages/DialogDetailPage.vue";
import { useAuthStore } from "@/store/auth";

const routes = [
  { path: "/", component: HomePage },
  { path: "/property/:id", component: PropertyDetailPage, props: true },
  { path: "/assistant", component: AssistantPage },
  { path: "/admin", component: AdminDashboard, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: "/agent", component: AdminDashboard, meta: { requiresAuth: true, requiresAgent: true } },
  { path: "/cabinet", component: CabinetPage, meta: { requiresAuth: true } },
  { path: "/favorites", component: FavoritesPage },
  { path: "/dialogs", component: DialogsPage, meta: { requiresAuth: true } },
  { path: "/dialogs/:id", component: DialogDetailPage, meta: { requiresAuth: true } },
  { path: "/login", component: LoginPage },
  { path: "/register", component: RegisterPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition;
    return { top: 0, left: 0 };
  },
});

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore();
  await auth.init();
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next({ path: "/login", query: { redirect: to.fullPath } });
  }
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return next(auth.isAuthenticated ? "/cabinet" : "/login");
  }
  if (to.meta.requiresAgent && !(auth.isAgent || auth.isAdmin)) {
    return next(auth.isAuthenticated ? "/cabinet" : "/login");
  }
  return next();
});

export default router;
