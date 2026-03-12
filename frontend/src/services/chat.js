import api from "@/services/api";

export const getConversations = async () => {
  const { data } = await api.get("/chat/conversations/");
  return data;
};

export const createConversation = async (listingId) => {
  const { data } = await api.post("/chat/conversations/", { listing_id: listingId });
  return data;
};

export const getConversationDetail = async (conversationId, limit = 50) => {
  const { data } = await api.get(`/chat/conversations/${conversationId}/`, {
    params: { limit },
  });
  return data;
};

export const getConversationMessages = async (conversationId, params = {}) => {
  const { data } = await api.get(`/chat/conversations/${conversationId}/messages/`, {
    params,
  });
  return data;
};

export const sendMessage = async (conversationId, text) => {
  const { data } = await api.post(`/chat/conversations/${conversationId}/messages/`, { text });
  return data;
};
