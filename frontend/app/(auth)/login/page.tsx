import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { LoginForm } from "@/features/auth/login-form";
import { safeNextPath } from "@/features/auth/validation";
import { getCurrentUser } from "@/lib/auth/dal";

export const metadata: Metadata = {
    title: "Iniciar sesión",
};

export default async function LoginPage({ searchParams }: PageProps<"/login">) {
    const params = await searchParams;
    const next = typeof params.next === "string" ? safeNextPath(params.next) : undefined;

    if (await getCurrentUser()) {
        redirect(next ?? "/app");
    }

    return (
        <>
            <h1 className="text-3xl font-semibold tracking-tight">Iniciar sesión</h1>
            <p className="mt-3 text-text-muted">
                {params.registered
                    ? "Su cuenta se creó correctamente. Inicie sesión para continuar."
                    : "Acceda a los casos y la evidencia de su organización."}
            </p>
            <div className="mt-8">
                <LoginForm next={next} />
            </div>
        </>
    );
}