"use client";

import { useId, useState } from "react";

import { inputStyles } from "@/components/forms/field-styles";
import { TextField } from "@/components/forms/text-field";

import { DESCRIPTION_MAX, TITLE_MAX, type CaseFormState } from "./form-state";

type CaseFieldsProps = {
  state: CaseFormState;
  autoFocus?: boolean;
};

/** Título y descripción del caso, compartidos por la creación y la edición. */
export function CaseFields({ state, autoFocus }: CaseFieldsProps) {
  const descriptionId = useId();
  const [description, setDescription] = useState(state.values.description);
  const remaining = DESCRIPTION_MAX - description.length;

  return (
    <div className="space-y-5">
      <TextField
        label="Título"
        name="title"
        required
        maxLength={TITLE_MAX}
        autoFocus={autoFocus}
        defaultValue={state.values.title}
        placeholder="Ej.: Proceso de alimentos — Gómez contra Ruiz"
        error={state.fieldErrors.title}
      />
      <div>
        <div className="flex items-baseline justify-between gap-4">
          <label htmlFor={descriptionId} className="text-sm font-medium">
            Descripción <span className="font-normal text-text-subtle">(opcional)</span>
          </label>
          <span className={`text-xs ${remaining < 200 ? "text-warning" : "text-text-subtle"}`}>
            {remaining.toLocaleString("es-CO")} restantes
          </span>
        </div>
        <textarea
          id={descriptionId}
          name="description"
          rows={4}
          maxLength={DESCRIPTION_MAX}
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          aria-invalid={state.fieldErrors.description ? true : undefined}
          className={`${inputStyles(Boolean(state.fieldErrors.description))} mt-2 resize-y`}
        />
        {state.fieldErrors.description && (
          <p className="mt-2 text-xs text-danger">{state.fieldErrors.description}</p>
        )}
      </div>
    </div>
  );
}
