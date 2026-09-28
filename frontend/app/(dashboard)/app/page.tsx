import type { Metadata } from "next";

import { Logo } from "@/components/brand/logo";
import { buttonStyles } from "@/components/ui/button-styles";
import { logout } from "@/features/auth/actions";
import { getApiClient, unwrap } from "@/lib/api/client";
import { requireAccessToken, requireUser } from "@/lib/auth/dal";
import { bearer } from "@/lib/auth/session";

export const metadata: Metadata = {
    title: "Inicio",
};

/** Inicio provisional del área privada, hasta construir el panel completo. */
export default async function AppHomePage() {
    const user = await requireUser();
    const token = await requireAccessToken();
    const organizations = await unwrap(
        getApiClient().GET("/api/v1/organizations", { headers: bearer(token) }),
    );

    return (
        <div className="mx-auto w-full max-w-3xl px-6 py-10">
            <header className="flex items-center justify-between gap-4">
                <Logo href="/app" />
                <form action={logout}>
                    <button type="submit" className={buttonStyles("ghost")}>
                        Cerrar sesión
                    </button>
                </form>
            </header>

            <main className="mt-16">
                <h1 className="text-3xl font-semibold tracking-tight">Hola, {user.full_name}</h1>
                <p className="mt-3 text-text-muted">Sesión iniciada como {user.email}.</p>

                <h2 className="mt-12 text-sm font-medium text-text-subtle">Sus organizaciones</h2>
                <ul className="mt-4 divide-y divide-border rounded-2xl border border-border bg-card/60">
                    {organizations.map((organization) => (
                        <li key={organization.id} className="flex items-center justify-between gap-4 p-5">
                            <span className="font-medium">{organization.name}</span>
                            <span className="text-sm text-text-muted">{organization.role}</span>
                        </li>
                    ))}
                </ul>
            </main>
        </div>
    );
}