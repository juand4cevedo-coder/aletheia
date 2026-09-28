import type { TokenPair } from "./tokens";

/**
 * Renovación de tokens para `proxy.ts`.
 *
 * La API revoca la sesión entera si recibe dos veces el mismo refresh token.
 * Si llegan varias peticiones a la vez con el mismo token, todas comparten
 * una única llamada. Es una protección en memoria: funciona con una sola
 * instancia del servidor de Next.js, que es el despliegue previsto.
 */
const inflight = new Map<string, Promise<TokenPair | null>>();

/** Tiempo que se conserva el resultado para peticiones que llegan tarde (ms). */
const RESULT_TTL_MS = 10_000;

async function requestRefresh(refreshToken: string): Promise<TokenPair | null> {
  const baseUrl = process.env.ALETHEIA_API_URL;
  if (!baseUrl) {
    throw new Error("ALETHEIA_API_URL is not configured.");
  }

  try {
    const response = await fetch(`${baseUrl}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
      cache: "no-store",
      signal: AbortSignal.timeout(10_000),
    });
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as TokenPair;
  } catch {
    return null;
  }
}

export function refreshTokens(refreshToken: string): Promise<TokenPair | null> {
  const existing = inflight.get(refreshToken);
  if (existing) {
    return existing;
  }

  const promise = requestRefresh(refreshToken);
  inflight.set(refreshToken, promise);
  setTimeout(() => inflight.delete(refreshToken), RESULT_TTL_MS);
  return promise;
}