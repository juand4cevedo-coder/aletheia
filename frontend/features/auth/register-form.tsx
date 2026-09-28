"use client";

import Link from "next/link";
import { useActionState, useState } from "react";

import { FormAlert } from "@/components/forms/form-alert";
import { PasswordField } from "@/components/forms/password-field";
import { SubmitButton } from "@/components/forms/submit-button";
import { TextField } from "@/components/forms/text-field";
import { buttonStyles } from "@/components/ui/button-styles";
import { getApiErrorMessage } from "@/lib/api/error-messages";

import { register } from "./actions";
import { INITIAL_AUTH_STATE, type AuthFormState } from "./form-state";
import { PASSWORD_MIN, validateEmail, validateName, validatePassword } from "./validation";

const STEP_ONE_FIELDS = ["full_name", "email", "password"] as const;

type Step = 1 | 2;

type RegisterFormProps = {
    planName?: string;
};

export function RegisterForm({ planName }: RegisterFormProps) {
    const [step, setStep] = useState<Step>(1);
    const [values, setValues] = useState({ full_name: "", email: "", password: "", organization_name: "" });
    const [localErrors, setLocalErrors] = useState<Partial<Record<string, string>>>({});

    const [state, formAction] = useActionState(
        async (previous: AuthFormState, formData: FormData) => {
            const result = await register(previous, formData);
            if (STEP_ONE_FIELDS.some((field) => result.fieldErrors[field])) {
                setStep(1);
            }
            setLocalErrors({});
            return result;
        },
        INITIAL_AUTH_STATE,
    );

    const errors = { ...state.fieldErrors, ...localErrors };

    function update(field: keyof typeof values, value: string) {
        setValues((current) => ({ ...current, [field]: value }));
        if (errors[field]) {
            setLocalErrors((current) => ({ ...current, [field]: undefined }));
        }
    }

    function continueToOrganization() {
        const found = {
            full_name: validateName(values.full_name.trim(), "su nombre"),
            email: validateEmail(values.email.trim()),
            password: validatePassword(values.password),
        };
        setLocalErrors(found);
        if (!found.full_name && !found.email && !found.password) {
            setStep(2);
        }
    }

    return (
        <form action={formAction} noValidate className="space-y-6">
            <ol aria-label="Pasos del registro" className="grid grid-cols-2 gap-3">
                {(["Su cuenta", "Su organización"] as const).map((label, index) => {
                    const number = (index + 1) as Step;
                    const active = step === number;
                    const done = step > number;
                    return (
                        <li key={label} aria-current={active ? "step" : undefined} className="space-y-2">
                            <div className={`h-1 rounded-full transition-colors ${active || done ? "bg-accent" : "bg-border"}`} />
                            <p className={`text-xs ${active ? "text-text" : "text-text-subtle"}`}>
                                <span className="font-mono">{number}.</span> {label}
                            </p>
                        </li>
                    );
                })}
            </ol>

            {planName && (
                <p className="rounded-lg border border-border bg-background px-4 py-3 text-sm text-text-muted">
                    Plan de interés: <span className="font-medium text-text">{planName}</span>.{" "}
                    <Link href="/#planes" className="text-accent hover:underline">
                        Cambiar
                    </Link>
                    <span className="mt-1 block text-xs text-text-subtle">
                        La facturación aún no está habilitada; la cuenta se crea sin cobro.
                    </span>
                </p>
            )}

            {state.code && <FormAlert message={getApiErrorMessage(state.code)} requestId={state.requestId} />}

            <div hidden={step !== 1} className="space-y-5">
                <TextField
                    label="Nombre completo"
                    name="full_name"
                    autoComplete="name"
                    value={values.full_name}
                    onChange={(event) => update("full_name", event.target.value)}
                    error={errors.full_name}
                />
                <TextField
                    label="Correo electrónico"
                    name="email"
                    type="email"
                    autoComplete="email"
                    inputMode="email"
                    value={values.email}
                    onChange={(event) => update("email", event.target.value)}
                    error={errors.email}
                />
                <PasswordField
                    label="Contraseña"
                    name="password"
                    autoComplete="new-password"
                    minLength={PASSWORD_MIN}
                    value={values.password}
                    onChange={(event) => update("password", event.target.value)}
                    error={errors.password}
                />
                <button
                    type="button"
                    onClick={continueToOrganization}
                    className={`${buttonStyles("primary", "lg")} w-full`}
                >
                    Continuar
                </button>
            </div>

            <div hidden={step !== 2} className="space-y-5">
                <TextField
                    label="Nombre de la firma u organización"
                    name="organization_name"
                    autoComplete="organization"
                    hint="Si trabaja de forma independiente, puede usar su propio nombre."
                    value={values.organization_name}
                    onChange={(event) => update("organization_name", event.target.value)}
                    error={errors.organization_name}
                />
                <p className="text-sm leading-6 text-text-muted">
                    Usted quedará como propietario de la organización y podrá crear casos
                    de inmediato.
                </p>
                <div className="flex flex-col-reverse gap-3 sm:flex-row">
                    <button
                        type="button"
                        onClick={() => setStep(1)}
                        className={`${buttonStyles("secondary", "lg")} sm:w-auto`}
                    >
                        Atrás
                    </button>
                    <SubmitButton pendingLabel="Creando cuenta…" className="sm:flex-1">
                        Crear cuenta
                    </SubmitButton>
                </div>
            </div>

            <p className="text-center text-sm text-text-muted">
                ¿Ya tiene cuenta?{" "}
                <Link href="/login" className="font-medium text-accent hover:underline">
                    Iniciar sesión
                </Link>
            </p>
        </form>
    );
}