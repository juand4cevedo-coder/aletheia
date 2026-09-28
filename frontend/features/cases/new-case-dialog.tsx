"use client";

import { useActionState, useRef } from "react";

import { FormAlert } from "@/components/forms/form-alert";
import { SubmitButton } from "@/components/forms/submit-button";
import { buttonStyles } from "@/components/ui/button-styles";
import { IconClose, IconPlus } from "@/components/ui/icons";
import { getApiErrorMessage } from "@/lib/api/error-messages";

import { createCase } from "./actions";
import { CaseFields } from "./case-fields";
import { initialCaseState } from "./form-state";

type NewCaseDialogProps = {
  organizationId: string;
  variant?: "primary" | "secondary";
};

/** Botón y diálogo modal para crear un caso. Usa `<dialog>` nativo: foco y Escape incluidos. */
export function NewCaseDialog({ organizationId, variant = "primary" }: NewCaseDialogProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [state, formAction] = useActionState(
    createCase.bind(null, organizationId),
    initialCaseState(),
  );

  return (
    <>
      <button type="button" onClick={() => dialogRef.current?.showModal()} className={buttonStyles(variant)}>
        <IconPlus className="size-4" />
        Nuevo caso
      </button>

      <dialog
        ref={dialogRef}
        aria-labelledby="new-case-title"
        onClick={(event) => {
          if (event.target === dialogRef.current) dialogRef.current.close();
        }}
        className="m-auto w-[min(34rem,calc(100%-2rem))] rounded-2xl border border-border bg-elevated p-0 text-text shadow-2xl shadow-black/50 backdrop:bg-background/70 backdrop:backdrop-blur-sm"
      >
        <form action={formAction} noValidate className="space-y-6 p-6 sm:p-8">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 id="new-case-title" className="text-xl font-semibold">
                Nuevo caso
              </h2>
              <p className="mt-1 text-sm text-text-muted">
                Usted quedará como responsable y podrá añadir miembros después.
              </p>
            </div>
            <button
              type="button"
              onClick={() => dialogRef.current?.close()}
              aria-label="Cerrar"
              className="rounded-lg p-2 text-text-subtle hover:bg-card hover:text-text"
            >
              <IconClose className="size-4" />
            </button>
          </div>

          {state.code && <FormAlert message={getApiErrorMessage(state.code)} requestId={state.requestId} />}

          <CaseFields key={state.requestId ?? "new"} state={state} autoFocus />

          <SubmitButton pendingLabel="Creando caso…">Crear caso</SubmitButton>
        </form>
      </dialog>
    </>
  );
}
