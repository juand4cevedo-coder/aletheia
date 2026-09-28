/**
 * Reglas de los formularios de cuenta. Replican las de la API para avisar
 * antes de enviar; la API sigue siendo la autoridad.
 */

export const PASSWORD_MIN = 15;
export const PASSWORD_MAX = 128;
export const NAME_MAX = 200;

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function validateEmail(value: string): string | undefined {
  if (!value) return "Escriba su correo electrónico.";
  if (!EMAIL_PATTERN.test(value)) return "Revise el formato del correo electrónico.";
  return undefined;
}

export function validatePassword(value: string): string | undefined {
  if (value.length < PASSWORD_MIN) return `La contraseña debe tener al menos ${PASSWORD_MIN} caracteres.`;
  if (value.length > PASSWORD_MAX) return `La contraseña no puede superar ${PASSWORD_MAX} caracteres.`;
  return undefined;
}

export function validateName(value: string, label: string): string | undefined {
  if (!value) return `Escriba ${label}.`;
  if (value.length > NAME_MAX) return `No puede superar ${NAME_MAX} caracteres.`;
  return undefined;
}

/** Solo se aceptan destinos internos del área privada, para evitar redirecciones abiertas. */
export function safeNextPath(value: FormDataEntryValue | string | null | undefined): string {
  if (typeof value === "string" && value.startsWith("/app") && !value.startsWith("//")) {
    return value;
  }
  return "/app";
}