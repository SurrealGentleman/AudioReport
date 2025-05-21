import axios from "axios";
import Cookies from "js-cookie";
import { logout } from "./authService";

const API_URL = "http://127.0.0.1:8000/api";

// Настраиваем axios
const api = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Разрешаем отправку cookies
});

// Функция обновления access-токена
const refreshAccessToken = async () => {
  const refreshToken = Cookies.get("refresh_token");

  if (!refreshToken) {
    logout();
    throw new Error("Refresh token not found");
  }

  try {
    const response = await api.post("/token/refresh/", {
      refresh: refreshToken,
    });
    console.log("new", response.data);
    Cookies.set("access_token", response.data.access, {
      path: "/",
      secure: false,
      httpOnly: false,
      sameSite: "Lax",
    });

    // Обновляем refresh-токен, если он пришёл в ответе
    if (response.data.refresh) {
      Cookies.set("refresh_token", response.data.refresh, {
        path: "/",
        secure: false,
        sameSite: "Lax",
        domain: window.location.hostname,
      });
    }

    return response.data.access;
  } catch (error) {
    console.error("Ошибка обновления:", error.response?.data || error.message);
    logout();
    throw error;
  }
};

// Интерцептор для автоматического обновления токена
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      originalRequest.url !== "/token/"
    ) {
      originalRequest._retry = true;
      console.log("i here", originalRequest.url);
      try {
        const newToken = await refreshAccessToken();
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        console.error("Ошибка обновления токена:", refreshError);
        logout();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
