"use server";

import { redirect } from "next/navigation";

import { getApiClient, expectNoContent, unwrap } from "@/lib/api/client";
import { getApiErrorMessage } from "@/lib/api/error-messages";
import { ApiError } from "@/lib/api/errors";
import { bearer, clearTokens, getAccessToken, saveTokens } from "@/lib/auth/session";

import type { AuthFormState } from "./form-state";
import { safeNextPath, validateEmail, validateName, validatePassword } from "./validation";

function text(formData: FormData, name: string): string {
  const value = formData.get(name);
  return typeof value === "string" ? value.trim() : "";
}

function rawText(formData: FormData, name: string): string {
  const value = formData.get(name);
  return typeof value === "string" ? value : "";
}

function withoutEmpty(errors: Record<string, string | undefined>): Partial<Record<string, string>> {
  return Object.fromEntries(Object.entries(errors).filter(([, message]) => message !== undefined));
}

/** Convierte un error de la API en estado de formulario; cualquier otro error se relanza. */
function fromApiError(
  error: unknown,
  values: Partial<Record<string, string>>,
  fieldForCode: Partial<Record<string, string>> = {},
): AuthFormState {
  if (!(error instanceof ApiError)) {
    throw error;
  }

  const fieldErrors: Partial<Record<string, string>> = {};
  for (const detail of error.details) {
    const field = detail.field.split(".").at(-1);
    if (field) {
      fieldErrors[field] = "Revise este campo.";
    }
  }
  const field = fieldForCode[error.code];
  if (field) {
    fieldErrors[field] = getApiErrorMessage(error.code);
    return { code: null, requestId: null, fieldErrors, values };
  }
  return { code: error.code, requestId: error.requestId, fieldErrors, values };
}

export async function login(_previous: AuthFormState, formData: FormData): Promise<AuthFormState> {
  const email = text(formData, "email");
  const password = rawText(formData, "password");
  const values = { email };

  const fieldErrors = withoutEmpty({
    email: validateEmail(email),
    password: password ? undefined : "Escriba su contraseña.",
  });
  if (Object.keys(fieldErrors).length > 0) {
    return { code: null, requestId: null, fieldErrors, values };
  }

  try {
    const pair = await unwrap(getApiClient().POST("/api/v1/auth/login", { body: { email, password } }));
    await saveTokens(pair);
  } catch (error) {
    return fromApiError(error, values);
  }

  redirect(safeNextPath(formData.get("next")));
}

export async function register(_previous: AuthFormState, formData: FormData): Promise<AuthFormState> {
  const fullName = text(formData, "full_name");
  const email = text(formData, "email");
  const password = rawText(formData, "password");
  const organizationName = text(formData, "organization_name");
  const values = { full_name: fullName, email, organization_name: organizationName };

  const fieldErrors = withoutEmpty({
    full_name: validateName(fullName, "su nombre"),
    email: validateEmail(email),
    password: validatePassword(password),
    organization_name: validateName(organizationName, "el nombre de la organización"),
  });
  if (Object.keys(fieldErrors).length > 0) {
    return { code: null, requestId: null, fieldErrors, values };
  }

  const api = getApiClient();
  try {
    await unwrap(
      api.POST("/api/v1/auth/register", {
        body: { email, password, full_name: fullName, organization_name: organizationName },
      }),
    );
  } catch (error) {
    return fromApiError(error, values, { EMAIL_ALREADY_REGISTERED: "email" });
  }

  // La cuenta ya existe: si el inicio de sesión automático falla, el login manual sigue disponible.
  try {
    const pair = await unwrap(api.POST("/api/v1/auth/login", { body: { email, password } }));
    await saveTokens(pair);
  } catch {
    redirect("/login?registered=1");
  }

  redirect("/app");
}

export async function logout(): Promise<void> {
  const token = await getAccessToken();
  if (token) {
    try {
      await expectNoContent(getApiClient().POST("/api/v1/auth/logout", { headers: bearer(token) }));
    } catch {
      // La sesión local se borra igualmente; si la API no respondió, el token caducará solo.
    }
  }
  await clearTokens();
  redirect("/login");
}