export type CaseFormState = {
  code: string | null;
  requestId: string | null;
  fieldErrors: Partial<Record<"title" | "description", string>>;
  values: { title: string; description: string };
  /** Marca de tiempo del último guardado correcto, para mostrar confirmación. */
  savedAt: number | null;
};

export function initialCaseState(values = { title: "", description: "" }): CaseFormState {
  return { code: null, requestId: null, fieldErrors: {}, values, savedAt: null };
}

export const TITLE_MAX = 200;
export const DESCRIPTION_MAX = 5000;
