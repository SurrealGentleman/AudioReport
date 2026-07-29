import axios from "axios";

import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  saveTokens,
} from "./tokenService";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

async function refreshAccessToken() {
  const refreshToken = getRefreshToken();

  if (!refreshToken) {
    clearTokens();
    throw new Error("Refresh token not found");
  }

  const response = await api.post("/auth/token/refresh/", {
    refresh: refreshToken,
  });

  saveTokens(response.data.access, response.data.refresh);

  return response.data.access;
}

api.interceptors.request.use((config) => {
  const accessToken = getAccessToken();

  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,

  async (error) => {
    const originalRequest = error.config;
    const requestUrl = originalRequest?.url;

    const isAuthenticationRequest =
      requestUrl === "/auth/token/" ||
      requestUrl === "/auth/token/refresh/";

    if (
      error.response?.status === 401 &&
      !originalRequest?._retry &&
      !isAuthenticationRequest
    ) {
      originalRequest._retry = true;

      try {
        const newAccessToken = await refreshAccessToken();

        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

        return api(originalRequest);
      } catch (refreshError) {
        clearTokens();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;