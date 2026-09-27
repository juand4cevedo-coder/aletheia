/**
 * Textos en español para cada `code` de error de la API.
 *
 * Este módulo no es `server-only`: la interfaz lo usa para mostrar errores.
 * La decisión de qué mostrar se toma siempre por `code`, nunca por el
 * `message` en inglés que envía la API.
 */

/** Código propio del frontend para respuestas que no siguen el formato de la API. */
export const UNEXPECTED_RESPONSE = "UNEXPECTED_RESPONSE";

const API_ERROR_MESSAGES = {
  NOT_AUTHENTICATED: "La sesión ha caducado. Es necesario iniciar sesión de nuevo.",
  INVALID_CREDENTIALS: "El correo electrónico o la contraseña no son correctos.",
  INVALID_REFRESH_TOKEN: "La sesión ha finalizado. Es necesario iniciar sesión de nuevo.",
  PERMISSION_DENIED: "Esta cuenta no tiene permiso para realizar esta acción.",
  NOT_FOUND: "El recurso solicitado no existe.",
  ORGANIZATION_NOT_FOUND: "La organización no existe o no está disponible para esta cuenta.",
  CASE_NOT_FOUND: "El caso no existe o no está disponible para esta cuenta.",
  CASE_MEMBER_NOT_FOUND: "Esta persona no es miembro del caso.",
  ORGANIZATION_MEMBER_NOT_FOUND:
    "Solo se pueden añadir al caso personas que ya pertenecen a la organización.",
  EVIDENCE_NOT_FOUND: "La evidencia no existe o no está disponible para esta cuenta.",
  METHOD_NOT_ALLOWED: "La operación solicitada no está disponible.",
  EMAIL_ALREADY_REGISTERED: "Ya existe una cuenta con este correo electrónico.",
  CASE_MEMBER_ALREADY_EXISTS: "Esta persona ya es miembro del caso.",
  LAST_CASE_LEAD:
    "Un caso no puede quedarse sin responsable. Primero hay que asignar otro responsable.",
  EVIDENCE_ALREADY_EXISTS:
    "Ya existe en este caso una evidencia con exactamente el mismo contenido (misma huella SHA-256).",
  CASE_NOT_ACTIVE: "Solo se puede añadir evidencia a casos activos.",
  FILE_TOO_LARGE: "El archivo supera el tamaño máximo de 100 MB.",
  UNSUPPORTED_FILE_TYPE: "Este tipo de archivo no se admite como evidencia.",
  FILE_TYPE_MISMATCH: "La extensión del archivo no corresponde a su contenido real.",
  VALIDATION_ERROR: "Algunos datos no son válidos. Los campos afectados están señalados.",
  EMPTY_FILE: "El archivo está vacío.",
  INTERNAL_ERROR: "Se produjo un error inesperado.",
  SERVICE_UNAVAILABLE:
    "El servicio no está disponible en este momento. Se puede volver a intentar en unos minutos.",
  EVIDENCE_STORAGE_UNAVAILABLE:
    "El archivo no se pudo guardar, por lo que no quedó preservado. Se puede volver a subir.",
  [UNEXPECTED_RESPONSE]: "Se recibió una respuesta inesperada del servidor.",
} as const satisfies Record<string, string>;

export type KnownApiErrorCode = keyof typeof API_ERROR_MESSAGES;

const FALLBACK_MESSAGE = "No se pudo completar la operación.";

export function isKnownApiErrorCode(code: string): code is KnownApiErrorCode {
  return Object.hasOwn(API_ERROR_MESSAGES, code);
}

/** Texto para el usuario; los códigos desconocidos reciben un mensaje genérico. */
export function getApiErrorMessage(code: string): string {
  return isKnownApiErrorCode(code) ? API_ERROR_MESSAGES[code] : FALLBACK_MESSAGE;
}
