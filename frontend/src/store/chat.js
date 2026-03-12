import { defineStore } from "pinia";
import {
  createConversation,
  getConversationDetail,
  getConversations,
  sendMessage,
} from "@/services/chat";
import { useAuthStore } from "@/store/auth";

const WS_BASE = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

const normalizeResults = (data) => {
  if (Array.isArray(data)) return data;
  if (data?.results) return data.results;
  return [];
};

export const useChatStore = defineStore("chat", {
  state: () => ({
    conversations: [],
    activeConversation: null,
    messages: [],
    loading: false,
    error: "",
    socket: null,
    reconnectAttempts: 0,
  }),
  actions: {
    reset() {
      this.conversations = [];
      this.activeConversation = null;
      this.messages = [];
      this.error = "";
      this.closeSocket();
    },
    async fetchConversations() {
      const auth = useAuthStore();
      if (!auth.isAuthenticated) {
        this.reset();
        return [];
      }
      this.loading = true;
      this.error = "";
      try {
        const data = await getConversations();
        this.conversations = normalizeResults(data);
        return this.conversations;
      } catch (error) {
        this.error = "Не удалось загрузить диалоги.";
        throw error;
      } finally {
        this.loading = false;
      }
    },
    async openConversation(conversationId) {
      this.loading = true;
      this.error = "";
      try {
        const data = await getConversationDetail(conversationId);
        this.activeConversation = data.conversation;
        this.messages = data.messages || [];
        this.connectSocket(conversationId);
      } catch (error) {
        this.error = "Не удалось открыть диалог.";
        throw error;
      } finally {
        this.loading = false;
      }
    },
    async startConversation(listingId) {
      const data = await createConversation(listingId);
      return data.conversation;
    },
    async sendMessage(text) {
      const conversationId = this.activeConversation?.id;
      if (!conversationId) return;
      const payload = { type: "message", text };
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify(payload));
        return;
      }
      const message = await sendMessage(conversationId, text);
      this.appendMessage(message);
    },
    appendMessage(message) {
      this.messages.push(message);
      if (this.activeConversation) {
        this.activeConversation.last_message_at = message.created_at;
      }
      const index = this.conversations.findIndex((item) => item.id === message.conversation_id);
      if (index >= 0) {
        const updated = {
          ...this.conversations[index],
          last_message: { text: message.text, created_at: message.created_at },
          last_message_at: message.created_at,
        };
        this.conversations.splice(index, 1);
        this.conversations.unshift(updated);
      }
    },
    connectSocket(conversationId) {
      this.closeSocket();
      const auth = useAuthStore();
      const token = auth.access || localStorage.getItem("access_token");
      if (!token) return;
      const url = `${WS_BASE}/ws/chat/${conversationId}/?token=${token}`;
      const socket = new WebSocket(url);
      this.socket = socket;
      this.reconnectAttempts = 0;

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "message") {
            this.appendMessage(data.message);
          }
        } catch (error) {
          // ignore malformed
        }
      };

      socket.onclose = () => {
        if (this.reconnectAttempts < 3) {
          this.reconnectAttempts += 1;
          setTimeout(() => this.connectSocket(conversationId), 800 * this.reconnectAttempts);
        }
      };
    },
    closeSocket() {
      if (this.socket) {
        this.socket.close();
        this.socket = null;
      }
    },
  },
});
