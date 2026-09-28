"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { getApiClient, unwrap } from "@/lib/api/client";
import { ApiError } from "@/lib/api/errors";
import { requireAccessToken } from "@/lib/auth/dal";
import { bearer } from "@/lib/auth/session";

import { DESCRIPTION_MAX, TITLE_MAX, type CaseFormState } from "./form-state";

function readValues(formData: FormData) {
  const title = formData.get("title");
  const description = formData.get("description");
  return {
    title: typeof title === "string" ? title.trim() : "",
    description: typeof description === "string" ? description.trim() : "",
  };
}

function validate(values: { title: string; description: string }): CaseFormState["fieldErrors"] {
  const errors: CaseFormState["fieldErrors"] = {};
  if (!values.title) errors.title = "Escriba un título para el caso.";
  else if (values.title.length > TITLE_MAX) errors.title = `El título no puede superar ${TITLE_MAX} caracteres.`;
  if (values.description.length > DESCRIPTION_MAX) {
    errors.description = `La descripción no puede superar ${DESCRIPTION_MAX} caracteres.`;
  }
  return errors;
}

function failure(error: unknown, values: CaseFormState["values"]): CaseFormState {
  if (!(error instanceof ApiError)) {
    throw error;
  }
  return { code: error.code, requestId: error.requestId, fieldErrors: {}, values, savedAt: null };
}

export async function createCase(
  organizationId: string,
  _previous: CaseFormState,
  formData: FormData,
): Promise<CaseFormState> {
  const values = readValues(formData);
  const fieldErrors = validate(values);
  if (Object.keys(fieldErrors).length > 0) {
    return { code: null, requestId: null, fieldErrors, values, savedAt: null };
  }

  const token = await requireAccessToken();
  let caseId: string;
  try {
    const created = await unwrap(
      getApiClient().POST("/api/v1/organizations/{organization_id}/cases", {
        headers: bearer(token),
        params: { path: { organization_id: organizationId } },
        body: { title: values.title, description: values.description || null },
      }),
    );
    caseId = created.id;
  } catch (error) {
    return failure(error, values);
  }

  revalidatePath(`/app/${organizationId}`, "layout");
  redirect(`/app/${organizationId}/cases/${caseId}`);
}

export async function updateCase(
  organizationId: string,
  caseId: string,
  _previous: CaseFormState,
  formData: FormData,
): Promise<CaseFormState> {
  const values = readValues(formData);
  const fieldErrors = validate(values);
  if (Object.keys(fieldErrors).length > 0) {
    return { code: null, requestId: null, fieldErrors, values, savedAt: null };
  }

  const token = await requireAccessToken();
  try {
    await unwrap(
      getApiClient().PATCH("/api/v1/organizations/{organization_id}/cases/{case_id}", {
        headers: bearer(token),
        params: { path: { organization_id: organizationId, case_id: caseId } },
        body: { title: values.title, description: values.description || null },
      }),
    );
  } catch (error) {
    return failure(error, values);
  }

  revalidatePath(`/app/${organizationId}`, "layout");
  return { code: null, requestId: null, fieldErrors: {}, values, savedAt: Date.now() };
}
