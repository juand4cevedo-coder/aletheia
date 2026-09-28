import "server-only";

import { cookies } from "next/headers";

import {
  ACCESS_COOKIE,
  REFRESH_COOKIE,
  accessCookieOptions,
  refreshCookieOptions,
} from "./cookies";
import type { TokenPair } from "./tokens";

/** Guarda la sesión en cookies. Solo en Server Actions y Route Handlers. */
export async function saveTokens(pair: TokenPair): Promise<void> {
  const store = await cookies();
  store.set(ACCESS_COOKIE, pair.access_token, accessCookieOptions(pair.expires_in));
  store.set(REFRESH_COOKIE, pair.refresh_token, refreshCookieOptions());
}

/** Borra la sesión. Solo en Server Actions y Route Handlers. */
export async function clearTokens(): Promise<void> {
  const store = await cookies();
  store.delete(ACCESS_COOKIE);
  store.delete(REFRESH_COOKIE);
}

export async function getAccessToken(): Promise<string | null> {
  const store = await cookies();
  return store.get(ACCESS_COOKIE)?.value ?? null;
}

export function bearer(token: string): { Authorization: string } {
  return { Authorization: `Bearer ${token}` };
}