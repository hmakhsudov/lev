import { defineStore } from "pinia";
import { addFavorite, getFavorites, removeFavorite } from "@/services/favorites";
import { useAuthStore } from "@/store/auth";

const normalizeResponse = (data) => {
  if (Array.isArray(data)) return data;
  if (data?.results && Array.isArray(data.results)) return data.results;
  return [];
};

export const useFavoritesStore = defineStore("favorites", {
  state: () => ({
    items: [],
    ids: [],
    loading: false,
    error: "",
  }),
  getters: {
    count: (state) => state.ids.length,
    isFavorited: (state) => (id) => state.ids.includes(Number(id)),
  },
  actions: {
    reset() {
      this.items = [];
      this.ids = [];
      this.error = "";
    },
    setFavorites(listings) {
      this.items = listings;
      this.ids = listings.map((item) => item.id);
    },
    async fetchFavorites() {
      const auth = useAuthStore();
      if (!auth.isAuthenticated) {
        this.reset();
        return [];
      }
      this.loading = true;
      this.error = "";
      try {
        const data = await getFavorites();
        const listings = normalizeResponse(data);
        this.setFavorites(listings);
        return listings;
      } catch (error) {
        this.error = "Не удалось загрузить избранное.";
        throw error;
      } finally {
        this.loading = false;
      }
    },
    async toggleFavorite(listing) {
      const auth = useAuthStore();
      if (!auth.isAuthenticated) {
        const error = new Error("AUTH_REQUIRED");
        error.code = "AUTH_REQUIRED";
        throw error;
      }
      const id = Number(listing?.id);
      if (!id) return;
      const currently = Boolean(listing?.is_favorited) || this.ids.includes(id);
      if (currently) {
        await removeFavorite(id);
        this.ids = this.ids.filter((item) => item !== id);
        this.items = this.items.filter((item) => item.id !== id);
        if (listing) listing.is_favorited = false;
      } else {
        await addFavorite(id);
        if (!this.ids.includes(id)) {
          this.ids = [id, ...this.ids];
        }
        if (listing && !this.items.find((item) => item.id === id)) {
          this.items = [listing, ...this.items];
        }
        if (listing) listing.is_favorited = true;
      }
    },
    syncWithListings(listings = []) {
      if (!Array.isArray(listings) || !this.ids.length) return;
      listings.forEach((item) => {
        if (!item) return;
        item.is_favorited = this.ids.includes(Number(item.id));
      });
    },
  },
});
