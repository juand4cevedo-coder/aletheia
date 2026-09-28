import "server-only";

import { redirect } from "next/navigation";
import { cache } from "react";

import { getApiClient, unwrap } from "@/lib/api/client";
import { ApiError } from "@/lib/api/errors";

import { bearer, getAccessToken } from "./session";

/**
 * Usuario de la sesión actual, o `null` si no hay sesión válida.
 * `cache` evita repetir la llamada a `/auth/me` dentro de una misma petición.
 */
export const getCurrentUser = cache(async () => {
  const token = await getAccessToken();
  if (!token) {
    return null;
  }
  try {
    return await unwrap(getApiClient().GET("/api/v1/auth/me", { headers: bearer(token) }));
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      return null;
    }
    throw error;
  }
});

/** Exige sesión: sin ella, redirige al login. */
export async function requireUser() {
  const user = await getCurrentUser();
  if (!user) {
    redirect("/login");
  }
  return user;
}

/** Token de acceso de una sesión que ya se sabe válida. */
export async function requireAccessToken(): Promise<string> {
  const token = await getAccessToken();
  if (!token) {
    redirect("/login");
  }
  return token;
}