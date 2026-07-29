import Cookies from "js-cookie";

const cookieOptions = {
  path: "/",
  secure: false,
  sameSite: "Lax",
};

export function getAccessToken() {
  return Cookies.get("access_token");
}

export function getRefreshToken() {
  return Cookies.get("refresh_token");
}

export function saveTokens(accessToken, refreshToken) {
  Cookies.set("access_token", accessToken, cookieOptions);

  if (refreshToken) {
    Cookies.set("refresh_token", refreshToken, cookieOptions);
  }
}

export function clearTokens() {
  Cookies.remove("access_token", { path: "/" });
  Cookies.remove("refresh_token", { path: "/" });
}