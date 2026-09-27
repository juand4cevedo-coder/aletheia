import "server-only";

import { UNEXPECTED_RESPONSE } from "./error-messages";

/** Error de validación de un campo, tal como lo devuelve la API en `details`. */
export type ApiFieldError = {
  readonly field: string;
  readonly message: string;
};

/**
 * Error normalizado de la API de Aletheia.
 *
 * `code` es la única base para decidir qué mostrar al usuario; `message`
 * viene en inglés desde la API y no se muestra.
 */
export class ApiError extends Error {
  override readonly name = "ApiError";
  readonly status: number;
  readonly code: string;
  readonly requestId: string | null;
  readonly details: readonly ApiFieldError[];

  constructor(options: {
    status: number;
    code: string;
    requestId: string | null;
    details?: readonly ApiFieldError[];
    cause?: unknown;
  }) {
    super(`API request failed: ${options.status} ${options.code}`, {
      cause: options.cause,
    });
    this.status = options.status;
    this.code = options.code;
    this.requestId = options.requestId;
    this.details = options.details ?? [];
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function parseDetails(value: unknown): ApiFieldError[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.flatMap((item: unknown) =>
    isRecord(item) &&
    typeof item.field === "string" &&
    typeof item.message === "string"
      ? [{ field: item.field, message: item.message }]
      : [],
  );
}

/**
 * Convierte una respuesta de error en `ApiError`.
 *
 * El cuerpo se trata como `unknown`: puede venir de la API, pero también de
 * un proxy intermedio (HTML, texto o vacío).
 */
export function toApiError(response: Response, body: unknown): ApiError {
  const payload = isRecord(body) ? body : {};
  const bodyRequestId =
    typeof payload.request_id === "string" ? payload.request_id : null;

  return new ApiError({
    status: response.status,
    code: typeof payload.code === "string" ? payload.code : UNEXPECTED_RESPONSE,
    requestId: response.headers.get("x-request-id") ?? bodyRequestId,
    details: parseDetails(payload.details),
  });
}
