import { defineStore } from "pinia";
import api from "@/services/api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("token"),
    user: null,
  }),
  actions: {
    async login(credentials) {
      const { data } = await api.post("/auth/login/", credentials);
      this.token = data.access;
      localStorage.setItem("token", data.access);
      await this.fetchCurrentUser();
    },
    async register(payload) {
      await api.post("/auth/register/", payload);
      await this.login({ email: payload.email, password: payload.password });
    },
    async fetchCurrentUser() {
      if (!this.token) return;
      const { data } = await api.get("/auth/me/");
      this.user = data;
    },
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem("token");
    },
  },
});
