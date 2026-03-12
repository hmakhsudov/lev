import api from "@/services/api";

export const getFavorites = async () => {
  const { data } = await api.get("/favorites/");
  return data;
};

export const addFavorite = async (listingId) => {
  const { data } = await api.post("/favorites/", { listing_id: listingId });
  return data;
};

export const removeFavorite = async (listingId) => {
  const { data } = await api.delete(`/favorites/${listingId}/`);
  return data;
};
