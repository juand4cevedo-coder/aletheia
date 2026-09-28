import { HashValue } from "@/components/ui/hash-value";

/** Huella SHA-256 de ejemplo: la del texto "Aletheia" en UTF-8. */
const SAMPLE_HASH = "7ca482c7004247c37e964367f8962a0b5f939b42ce2ab188cf5653c466fe3786";

const FACTS = [
    "El original se guarda sin posibilidad de sobrescritura.",
    "Cada archivo queda con su huella SHA-256.",
    "Solo los miembros de cada caso pueden verlo.",
] as const;

/** Panel lateral de las páginas de acceso. */
export function AuthShowcase() {
    return (
        <div className="flex h-full flex-col justify-between gap-12 p-10 xl:p-14">
            <div>
                <p className="text-xs font-medium tracking-[0.18em] text-accent uppercase">
                    Evidencia digital
                </p>
                <p className="mt-5 max-w-md text-4xl leading-[1.1] font-semibold tracking-tight text-balance">
                    Cada evidencia, con su huella y su historia.
                </p>
                <ul className="mt-10 space-y-4">
                    {FACTS.map((fact) => (
                        <li key={fact} className="flex gap-3 text-text-muted">
                            <svg aria-hidden="true" viewBox="0 0 16 16" className="mt-1 size-4 shrink-0 text-accent" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="m3.5 8.5 3 3 6-7" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                            {fact}
                        </li>
                    ))}
                </ul>
            </div>

            <figure className="rounded-2xl border border-border bg-background/60 p-5">
                <figcaption className="text-xs text-text-subtle">
                    SHA-256 de la palabra «Aletheia»
                </figcaption>
                <HashValue value={SAMPLE_HASH} className="mt-3 text-text-muted" />
            </figure>
        </div>
    );
}