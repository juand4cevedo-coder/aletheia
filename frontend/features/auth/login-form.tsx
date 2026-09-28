"use client";

import Link from "next/link";
import { useActionState } from "react";

import { FormAlert } from "@/components/forms/form-alert";
import { PasswordField } from "@/components/forms/password-field";
import { SubmitButton } from "@/components/forms/submit-button";
import { TextField } from "@/components/forms/text-field";
import { getApiErrorMessage } from "@/lib/api/error-messages";

import { login } from "./actions";
import { INITIAL_AUTH_STATE } from "./form-state";

type LoginFormProps = {
    next?: string;
};

export function LoginForm({ next }: LoginFormProps) {
    const [state, formAction] = useActionState(login, INITIAL_AUTH_STATE);

    return (
        <form action={formAction} noValidate className="space-y-5">
            {state.code && (
                <FormAlert
                    message={getApiErrorMessage(state.code)}
                    requestId={state.code === "INVALID_CREDENTIALS" ? null : state.requestId}
                />
            )}

            {next && <input type="hidden" name="next" value={next} />}

            <TextField
                label="Correo electrónico"
                name="email"
                type="email"
                autoComplete="email"
                inputMode="email"
                autoFocus
                required
                defaultValue={state.values.email}
                error={state.fieldErrors.email}
            />
            <PasswordField
                label="Contraseña"
                name="password"
                autoComplete="current-password"
                required
                error={state.fieldErrors.password}
            />

            <SubmitButton pendingLabel="Iniciando sesión…">Iniciar sesión</SubmitButton>

            <p className="text-center text-sm text-text-muted">
                ¿Aún no tiene cuenta?{" "}
                <Link href="/register" className="font-medium text-accent hover:underline">
                    Crear cuenta
                </Link>
            </p>
        </form>
    );
}