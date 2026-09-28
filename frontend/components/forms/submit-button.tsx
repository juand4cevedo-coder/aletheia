"use client";

import type { ReactNode } from "react";
import { useFormStatus } from "react-dom";

import { buttonStyles } from "@/components/ui/button-styles";

type SubmitButtonProps = {
    children: ReactNode;
    pendingLabel: string;
    className?: string;
};

/** Botón de envío que se bloquea y muestra progreso mientras el formulario se procesa. */
export function SubmitButton({ children, pendingLabel, className = "" }: SubmitButtonProps) {
    const { pending } = useFormStatus();

    return (
        <button
            type="submit"
            disabled={pending}
            aria-disabled={pending}
            className={`${buttonStyles("primary", "lg")} w-full ${className}`}
        >
            {pending && (
                <span
                    aria-hidden="true"
                    className="size-4 animate-spin rounded-full border-2 border-on-accent/30 border-t-on-accent"
                />
            )}
            {pending ? pendingLabel : children}
        </button>
    );
}