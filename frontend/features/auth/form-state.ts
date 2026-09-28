/** Estado que devuelven las Server Actions de autenticación al formulario. */
export type AuthFormState = {
  /** `code` de error de la API (o propio), `null` si no hubo error general. */
  code: string | null;
  requestId: string | null;
  /** Errores por campo, ya en español. */
  fieldErrors: Partial<Record<string, string>>;
  /** Valores a conservar en el formulario (nunca la contraseña). */
  values: Partial<Record<string, string>>;
};

export const INITIAL_AUTH_STATE: AuthFormState = {
  code: null,
  requestId: null,
  fieldErrors: {},
  values: {},
};