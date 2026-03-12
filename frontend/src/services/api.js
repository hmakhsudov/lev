import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";

export const getAccessToken = () => localStorage.getItem(ACCESS_TOKEN_KEY);
export const getRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY);
export const setAccessToken = (token) => localStorage.setItem(ACCESS_TOKEN_KEY, token);
export const setRefreshToken = (token) => localStorage.setItem(REFRESH_TOKEN_KEY, token);
export const clearTokens = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

const api = axios.create({
  baseURL: API_BASE,
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original?._retry) {
      original._retry = true;
      const refresh = getRefreshToken();
      if (!refresh) {
        clearTokens();
        return Promise.reject(error);
      }
      try {
        const { data } = await axios.post(`${API_BASE}/auth/refresh/`, { refresh });
        if (data?.access) {
          setAccessToken(data.access);
          original.headers.Authorization = `Bearer ${data.access}`;
          return api(original);
        }
      } catch (refreshError) {
        clearTokens();
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
