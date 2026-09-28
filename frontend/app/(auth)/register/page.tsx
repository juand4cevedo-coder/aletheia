import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { PLANS } from "@/features/landing/plans";
import { RegisterForm } from "@/features/auth/register-form";
import { getCurrentUser } from "@/lib/auth/dal";

export const metadata: Metadata = {
    title: "Crear cuenta",
};

export default async function RegisterPage({ searchParams }: PageProps<"/register">) {
    if (await getCurrentUser()) {
        redirect("/app");
    }

    const { plan } = await searchParams;
    const planName = PLANS.find((item) => item.id === plan)?.name;

    return (
        <>
            <h1 className="text-3xl font-semibold tracking-tight">Crear cuenta</h1>
            <p className="mt-3 text-text-muted">
                Cree su cuenta y la de su organización. Después podrá abrir su primer caso.
            </p>
            <div className="mt-8">
                <RegisterForm planName={planName} />
            </div>
        </>
    );
}