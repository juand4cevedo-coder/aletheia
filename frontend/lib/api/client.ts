import "server-only";

import createClient, { type Client } from "openapi-fetch";

import { UNEXPECTED_RESPONSE } from "./error-messages";
import { ApiError, toApiError } from "./errors";
import type { paths } from "./schema";

/** Tiempo máximo de espera por petición a la API (ms). */
const REQUEST_TIMEOUT_MS = 15_000;

let client: Client<paths> | undefined;

function readApiBaseUrl(): string {
  const value = process.env.ALETHEIA_API_URL;
  if (!value) {
    throw new Error("ALETHEIA_API_URL is not configured.");
  }
  return value;
}

/**
 * Cliente tipado de la API de Aletheia. Solo existe en el servidor.
 *
 * Se crea de forma perezosa para que importar este módulo no exija la
 * variable de entorno (por ejemplo, durante `next build` en la CI).
 */
export function getApiClient(): Client<paths> {
  client ??= createClient<paths>({
    baseUrl: readApiBaseUrl(),
    cache: "no-store",
    fetch: (request) =>
      fetch(request, {
        signal: AbortSignal.any([
          request.signal,
          AbortSignal.timeout(REQUEST_TIMEOUT_MS),
        ]),
      }),
  });
  return client;
}

type ApiResult<T> = {
  data?: T;
  error?: unknown;
  response: Response;
};

async function send<T>(request: Promise<ApiResult<T>>): Promise<ApiResult<T>> {
  let result: ApiResult<T>;
  try {
    result = await request;
  } catch (cause) {
    // Red caída, DNS, timeout o conexión rechazada: no hubo respuesta HTTP.
    throw new ApiError({
      status: 503,
      code: "SERVICE_UNAVAILABLE",
      requestId: null,
      cause,
    });
  }
  if (!result.response.ok) {
    throw toApiError(result.response, result.error);
  }
  return result;
}

/**
 * Espera una petición de `openapi-fetch` y devuelve su cuerpo.
 * Lanza `ApiError` si la API respondió con error, no pudo ser contactada
 * o respondió con éxito pero sin cuerpo.
 */
export async function unwrap<T>(request: Promise<ApiResult<T>>): Promise<T> {
  const { data, response } = await send(request);
  if (data === undefined) {
    throw new ApiError({
      status: response.status,
      code: UNEXPECTED_RESPONSE,
      requestId: response.headers.get("x-request-id"),
    });
  }
  return data;
}

/** Para endpoints que responden 204 sin cuerpo (por ejemplo, logout). */
export async function expectNoContent(
  request: Promise<ApiResult<unknown>>,
): Promise<void> {
  await send(request);
}
