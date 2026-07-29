import { useState } from "react";
import AuthContext from "./authContext";

import {
  login as loginRequest,
  logout as logoutRequest,
} from "../services/authService";
import { getAccessToken } from "../services/tokenService";


function getStoredUser() {
  const storedUser = localStorage.getItem("user");

  if (!storedUser) {
    return null;
  }

  try {
    return JSON.parse(storedUser);
  } catch {
    localStorage.removeItem("user");
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(getStoredUser);

  const isAuthenticated = Boolean(getAccessToken() && user);

  async function login(email, password) {
    const data = await loginRequest(email, password);

    if (!data.user) {
      throw new Error("Backend не вернул данные пользователя");
    }

    localStorage.setItem("user", JSON.stringify(data.user));
    setUser(data.user);

    return data.user;
  }

  function logout() {
    logoutRequest();
    localStorage.removeItem("user");
    setUser(null);
  }

  const value = {
    user,
    isAuthenticated,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
