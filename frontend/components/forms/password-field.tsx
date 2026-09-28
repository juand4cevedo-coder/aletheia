"use client";

import { useId, useState, type InputHTMLAttributes } from "react";

import { inputStyles } from "./field-styles";

type PasswordFieldProps = Omit<InputHTMLAttributes<HTMLInputElement>, "id" | "type"> & {
    label: string;
    name: string;
    error?: string;
    /** Si se indica, muestra el progreso hacia la longitud mínima. */
    minLength?: number;
    value?: string;
};

/** Contraseña con botón para mostrarla y, opcionalmente, progreso de longitud. */
export function PasswordField({ label, name, error, minLength, value, ...inputProps }: PasswordFieldProps) {
    const id = useId();
    const errorId = `${id}-error`;
    const progressId = `${id}-progress`;
    const [visible, setVisible] = useState(false);
    const length = value?.length ?? 0;
    const showProgress = minLength !== undefined && value !== undefined;
    const complete = showProgress && length >= minLength;
    const describedBy = [showProgress && progressId, error && errorId].filter(Boolean).join(" ") || undefined;

    return (
        <div>
            <label htmlFor={id} className="block text-sm font-medium">
                {label}
            </label>
            <div className="relative mt-2">
                <input
                    id={id}
                    name={name}
                    type={visible ? "text" : "password"}
                    value={value}
                    minLength={minLength}
                    aria-invalid={error ? true : undefined}
                    aria-describedby={describedBy}
                    className={`${inputStyles(Boolean(error))} pr-24`}
                    {...inputProps}
                />
                <button
                    type="button"
                    onClick={() => setVisible((current) => !current)}
                    aria-pressed={visible}
                    aria-controls={id}
                    className="absolute inset-y-1 right-1 rounded-md px-3 text-xs font-medium text-text-muted hover:bg-card hover:text-text"
                >
                    {visible ? "Ocultar" : "Mostrar"}
                </button>
            </div>

            {showProgress && (
                <div id={progressId} className="mt-3">
                    <div
                        aria-hidden="true"
                        className="h-1 overflow-hidden rounded-full bg-border"
                    >
                        <div
                            className={`h-full rounded-full transition-[width,background-color] duration-300 ${complete ? "bg-success" : "bg-accent"}`}
                            style={{ width: `${Math.min(length / minLength, 1) * 100}%` }}
                        />
                    </div>
                    <p className={`mt-2 text-xs ${complete ? "text-success" : "text-text-subtle"}`}>
                        {complete
                            ? "Longitud suficiente. Una frase larga es más segura que una palabra complicada."
                            : `${length} de ${minLength} caracteres como mínimo. Puede usar una frase.`}
                    </p>
                </div>
            )}

            {error && (
                <p id={errorId} className="mt-2 text-xs text-danger">
                    {error}
                </p>
            )}
        </div>
    );
}