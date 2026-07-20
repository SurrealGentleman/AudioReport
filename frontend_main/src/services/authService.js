import api from "./api";
import { clearTokens, saveTokens } from "./tokenService";

export async function login(email, password) {
  const response = await api.post("/auth/token/", {
    email,
    password,
  });

  saveTokens(response.data.access, response.data.refresh);

  return response.data;
}

export function logout() {
  clearTokens();
}