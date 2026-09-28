import Link from "next/link";

import { buttonStyles } from "@/components/ui/button-styles";

export function CallToAction() {
    return (
        <section aria-labelledby="cta-title" className="mx-auto w-full max-w-6xl px-6 pt-8 pb-28">
            <div className="rounded-3xl border border-border bg-[radial-gradient(40rem_20rem_at_85%_0%,color-mix(in_oklab,var(--brand)_35%,transparent),transparent)] bg-elevated p-8 sm:p-14">
                <h2
                    id="cta-title"
                    className="max-w-2xl text-4xl leading-[1.05] font-semibold tracking-tight text-balance sm:text-5xl"
                >
                    Preserve su primera evidencia hoy.
                </h2>
                <p className="mt-6 max-w-xl text-lg leading-8 text-text-muted">
                    Cree la cuenta de su firma, abra un caso e incorpore un archivo. Al
                    terminar la subida tendrá su huella SHA-256 y el registro de su
                    preservación.
                </p>
                <div className="mt-10 flex flex-wrap gap-3">
                    <Link href="/register" className={buttonStyles("primary", "lg")}>
                        Crear cuenta
                    </Link>
                    <Link href="/login" className={buttonStyles("secondary", "lg")}>
                        Iniciar sesión
                    </Link>
                </div>
            </div>
        </section>
    );
}