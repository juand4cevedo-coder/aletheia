"use client";

import { useActionState, useState } from "react";

import { FormAlert } from "@/components/forms/form-alert";
import { SubmitButton } from "@/components/forms/submit-button";
import { buttonStyles } from "@/components/ui/button-styles";
import { getApiErrorMessage } from "@/lib/api/error-messages";

import { updateCase } from "./actions";
import { CaseFields } from "./case-fields";
import { initialCaseState, type CaseFormState } from "./form-state";

type CaseEditorProps = {
  organizationId: string;
  caseId: string;
  title: string;
  description: string | null;
};

/** Edición del título y la descripción, en el mismo lugar donde se leen. */
export function CaseEditor({ organizationId, caseId, title, description }: CaseEditorProps) {
  const [editing, setEditing] = useState(false);
  const [state, formAction] = useActionState(
    async (previous: CaseFormState, formData: FormData) => {
      const result = await updateCase(organizationId, caseId, previous, formData);
      if (result.savedAt) setEditing(false);
      return result;
    },
    initialCaseState({ title, description: description ?? "" }),
  );

  const hasErrors = state.code !== null || Object.keys(state.fieldErrors).length > 0;

  if (!editing) {
    return (
      <div>
        <h1 className="text-3xl leading-tight font-semibold tracking-tight text-balance sm:text-4xl">{title}</h1>
        {description ? (
          <p className="mt-4 max-w-3xl leading-7 whitespace-pre-line text-text-muted">{description}</p>
        ) : (
          <p className="mt-4 text-sm text-text-subtle">Sin descripción.</p>
        )}
        <div className="mt-5 flex items-center gap-4">
          <button type="button" onClick={() => setEditing(true)} className={buttonStyles("secondary")}>
            Editar datos del caso
          </button>
          {state.savedAt && (
            <p role="status" className="text-sm text-success">
              Cambios guardados.
            </p>
          )}
        </div>
      </div>
    );
  }

  return (
    <form action={formAction} noValidate className="max-w-2xl space-y-5 rounded-2xl border border-border bg-card/60 p-6">
      {state.code && <FormAlert message={getApiErrorMessage(state.code)} requestId={state.requestId} />}
      <CaseFields state={hasErrors ? state : { ...state, values: { title, description: description ?? "" } }} autoFocus />
      <div className="flex flex-col-reverse gap-3 sm:flex-row">
        <button type="button" onClick={() => setEditing(false)} className={buttonStyles("secondary", "lg")}>
          Cancelar
        </button>
        <SubmitButton pendingLabel="Guardando…" className="sm:flex-1">
          Guardar cambios
        </SubmitButton>
      </div>
    </form>
  );
}
