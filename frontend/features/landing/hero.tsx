import Link from "next/link";

import { buttonStyles } from "@/components/ui/button-styles";
import { StatusBadge } from "@/components/ui/status-badge";

const STAGES = [
    { name: "Archivo", detail: "Se incorpora al caso correspondiente.", available: true },
    { name: "Validación", detail: "Se comprueba el tipo real por su contenido.", available: true },
    { name: "Huella SHA-256", detail: "Se calcula sobre el contenido exacto.", available: true },
    { name: "Preservación", detail: "El original se guarda sin sobrescritura.", available: true },
    { name: "Historial de eventos", detail: "Cada operación queda encadenada.", available: false },
    { name: "Verificación e informe", detail: "Se compara la huella y se documenta.", available: false },
] as const;

export function Hero() {
    return (
        <section
            aria-labelledby="hero-title"
            className="relative overflow-hidden bg-[radial-gradient(60rem_30rem_at_20%_-10%,color-mix(in_oklab,var(--brand)_30%,transparent),transparent)]"
        >
            <div className="mx-auto grid w-full max-w-6xl items-center gap-16 px-6 pt-20 pb-24 lg:grid-cols-[1.15fr_1fr] lg:pt-28 lg:pb-32">
                <div>
                    <p className="inline-flex rounded-full border border-border-strong px-3 py-1 text-xs font-medium tracking-[0.18em] text-accent uppercase">
                        Evidencia digital
                    </p>
                    <h1
                        id="hero-title"
                        className="mt-6 text-5xl leading-[1.02] font-semibold tracking-tight text-balance sm:text-6xl lg:text-7xl"
                    >
                        Evidencia con una historia verificable.
                    </h1>
                    <p className="mt-8 max-w-xl text-lg leading-8 text-text-muted">
                        Aletheia preserva cada archivo con su huella SHA-256 y documenta quién
                        lo incorporó, cuándo y en qué caso. El original no se sobrescribe, y
                        su huella permite comprobar después que el contenido sigue siendo el
                        mismo.
                    </p>
                    <div className="mt-10 flex flex-wrap gap-3">
                        <Link href="/register" className={buttonStyles("primary", "lg")}>
                            Crear cuenta
                        </Link>
                        <Link href="/#como-funciona" className={buttonStyles("secondary", "lg")}>
                            Ver cómo funciona
                        </Link>
                    </div>
                </div>

                <div className="rounded-2xl border border-border bg-card/70 p-6 shadow-2xl shadow-black/30 sm:p-8">
                    <div className="flex items-center justify-between gap-4 border-b border-border pb-5">
                        <h2 className="font-medium">Recorrido de una evidencia</h2>
                        <span className="text-xs text-text-subtle">6 etapas</span>
                    </div>
                    <ol className="mt-2">
                        {STAGES.map((stage, index) => (
                            <li key={stage.name} className="relative flex gap-4 py-3.5">
                                {index < STAGES.length - 1 && (
                                    <span
                                        aria-hidden="true"
                                        className="absolute top-11 bottom-0 left-4 w-px -translate-x-1/2 bg-border-strong"
                                    />
                                )}
                                <span
                                    aria-hidden="true"
                                    className={`relative flex size-8 shrink-0 items-center justify-center rounded-full border font-mono text-xs ${stage.available
                                            ? "border-accent/60 bg-elevated text-accent"
                                            : "border-border-strong bg-elevated text-text-subtle"
                                        }`}
                                >
                                    {index + 1}
                                </span>
                                <div className="flex min-w-0 flex-1 flex-col items-start gap-2 sm:flex-row sm:justify-between sm:gap-4">
                                    <div className="min-w-0">
                                        <p className="font-medium">{stage.name}</p>
                                        <p className="mt-0.5 text-sm text-text-muted">{stage.detail}</p>
                                    </div>
                                    <span className="shrink-0">
                                        <StatusBadge tone={stage.available ? "available" : "upcoming"} />
                                    </span>
                                </div>
                            </li>
                        ))}
                    </ol>
                </div>
            </div>
        </section>
    );
}