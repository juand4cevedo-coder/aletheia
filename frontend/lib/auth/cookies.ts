export const ACCESS_COOKIE = "aletheia_access";
export const REFRESH_COOKIE = "aletheia_refresh";

/** Duración máxima de una sesión en la API (14 días). */
const SESSION_MAX_AGE_SECONDS = 14 * 24 * 60 * 60;

/** La cookie de acceso caduca antes que el token para no enviar uno vencido. */
const ACCESS_EXPIRY_MARGIN_SECONDS = 30;

type CookieOptions = {
  httpOnly: true;
  secure: boolean;
  sameSite: "strict";
  path: "/";
  maxAge: number;
};

function baseOptions(maxAge: number): CookieOptions {
  return {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    path: "/",
    maxAge,
  };
}

export function accessCookieOptions(expiresIn: number): CookieOptions {
  return baseOptions(Math.max(expiresIn - ACCESS_EXPIRY_MARGIN_SECONDS, 1));
}

export function refreshCookieOptions(): CookieOptions {
  return baseOptions(SESSION_MAX_AGE_SECONDS);
}