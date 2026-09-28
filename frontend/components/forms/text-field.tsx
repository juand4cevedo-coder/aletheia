import { useId, type InputHTMLAttributes } from "react";

import { inputStyles } from "./field-styles";

type TextFieldProps = Omit<InputHTMLAttributes<HTMLInputElement>, "id"> & {
    label: string;
    name: string;
    error?: string;
    hint?: string;
};

/** Campo de texto con etiqueta, ayuda y error enlazados para lectores de pantalla. */
export function TextField({ label, name, error, hint, className = "", ...inputProps }: TextFieldProps) {
    const id = useId();
    const hintId = `${id}-hint`;
    const errorId = `${id}-error`;
    const describedBy = [hint && hintId, error && errorId].filter(Boolean).join(" ") || undefined;

    return (
        <div className={className}>
            <label htmlFor={id} className="block text-sm font-medium">
                {label}
            </label>
            <input
                id={id}
                name={name}
                aria-invalid={error ? true : undefined}
                aria-describedby={describedBy}
                className={`${inputStyles(Boolean(error))} mt-2`}
                {...inputProps}
            />
            {hint && !error && (
                <p id={hintId} className="mt-2 text-xs text-text-subtle">
                    {hint}
                </p>
            )}
            {error && (
                <p id={errorId} className="mt-2 text-xs text-danger">
                    {error}
                </p>
            )}
        </div>
    );
}