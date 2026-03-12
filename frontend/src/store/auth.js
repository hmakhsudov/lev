import { defineStore } from "pinia";
import api, {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setAccessToken,
  setRefreshToken,
} from "@/services/api";

const USER_KEY = "auth_user";

function parseError(error) {
  const data = error?.response?.data;
  if (!data) return "Ошибка авторизации";
  if (data.detail) return data.detail;
  if (typeof data === "string") return data;
  if (typeof data === "object") {
    const firstKey = Object.keys(data)[0];
    const value = data[firstKey];
    if (Array.isArray(value)) return value[0];
    if (typeof value === "string") return value;
  }
  return "Ошибка авторизации";
}

export const useAuthStore = defineStore("auth", {
  state: () => ({
    access: getAccessToken() || localStorage.getItem("token"),
    refresh: getRefreshToken(),
    user: (() => {
      try {
        const raw = localStorage.getItem(USER_KEY);
        return raw ? JSON.parse(raw) : null;
      } catch (e) {
        return null;
      }
    })(),
    loading: false,
    error: "",
    initialized: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.access),
    isAdmin: (state) => state.user?.role === "admin",
    isAgent: (state) => state.user?.role === "agent",
  },
  actions: {
    setSession({ access, refresh, user }) {
      if (access) {
        this.access = access;
        setAccessToken(access);
      }
      if (refresh) {
        this.refresh = refresh;
        setRefreshToken(refresh);
      }
      if (user) {
        this.user = user;
        localStorage.setItem(USER_KEY, JSON.stringify(user));
      }
    },
    clearSession() {
      this.access = null;
      this.refresh = null;
      this.user = null;
      clearTokens();
      localStorage.removeItem(USER_KEY);
    },
    async init() {
      if (this.initialized) return;
      this.initialized = true;
      if (this.access && !getAccessToken()) {
        setAccessToken(this.access);
        localStorage.removeItem("token");
      }
      if (this.access && !this.user) {
        try {
          await this.fetchCurrentUser();
        } catch (e) {
          this.clearSession();
        }
      }
    },
    async login(credentials) {
      this.loading = true;
      this.error = "";
      try {
        const { data } = await api.post("/auth/login/", credentials);
        this.setSession({
          access: data.access,
          refresh: data.refresh,
          user: data.user,
        });
        return data.user;
      } catch (e) {
        if (import.meta.env.DEV) {
          console.error("login error", e?.response?.data || e);
        }
        this.error = parseError(e);
        throw e;
      } finally {
        this.loading = false;
      }
    },
    async register(payload) {
      this.loading = true;
      this.error = "";
      try {
        const { data } = await api.post("/auth/register/", payload);
        this.setSession({
          access: data.access,
          refresh: data.refresh,
          user: data.user,
        });
        return data.user;
      } catch (e) {
        if (import.meta.env.DEV) {
          console.error("register error", e?.response?.data || e);
        }
        this.error = parseError(e);
        throw e;
      } finally {
        this.loading = false;
      }
    },
    async fetchCurrentUser() {
      if (!this.access) return null;
      const { data } = await api.get("/auth/me/");
      this.user = data;
      localStorage.setItem(USER_KEY, JSON.stringify(data));
      return data;
    },
    async updateProfile(payload) {
      this.loading = true;
      this.error = "";
      try {
        const { data } = await api.patch("/auth/me/", payload);
        this.user = data;
        localStorage.setItem(USER_KEY, JSON.stringify(data));
        return data;
      } catch (e) {
        if (import.meta.env.DEV) {
          console.error("update profile error", e?.response?.data || e);
        }
        this.error = parseError(e);
        throw e;
      } finally {
        this.loading = false;
      }
    },
    logout() {
      this.clearSession();
    },
  },
});
