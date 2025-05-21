import api from "./api";
import Cookies from "js-cookie";

// Функция логина
export const login = async (email, password) => {
  const response = await api.post("/token/", {
    email: email,
    password: password,
  });
  Cookies.set("access_token", response.data.access, {
    secure: false,
    httpOnly: false,
  });
  Cookies.set("refresh_token", response.data.refresh, {
    secure: false,
    httpOnly: false,
  });
  return response.data;
};

// Функция выхода
export const logout = () => {
  Cookies.remove("access_token");
  Cookies.remove("refresh_token");
};

// Получение данных профиля (защищённый API)
// export const getProfile = async () => {
//   const response = await api.get("/protected/");
//   return response.data;
// };
