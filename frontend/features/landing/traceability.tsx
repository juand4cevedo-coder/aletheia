import { SectionHeading } from "@/components/ui/section-heading";
import { StatusBadge } from "@/components/ui/status-badge";

const EVENTS = [
    {
        name: "Evidencia preservada",
        detail: "Queda registrado quién incorporó el archivo, cuándo y en qué caso.",
        available: true,
    },
    {
        name: "Evidencia consultada o descargada",
        detail: "Cada acceso al original queda asociado a un usuario y un momento.",
        available: false,
    },
    {
        name: "Integridad verificada",
        detail: "El resultado de cada comparación de huellas pasa a formar parte del historial.",
        available: false,
    },
    {
        name: "Informe generado",
        detail: "La emisión de un informe de preservación también se registra.",
        available: false,
    },
] as const;

export function Traceability() {
    return (
        <section
            aria-labelledby="trazabilidad-title"
            id="trazabilidad"
            className="mx-auto grid w-full max-w-6xl scroll-mt-20 gap-16 px-6 py-24 lg:grid-cols-[1fr_1.1fr]"
        >
            <div>
                <SectionHeading
                    id="trazabilidad-title"
                    eyebrow="Trazabilidad"
                    title="Los eventos construyen una historia verificable."
                    intro="Cada operación relevante sobre una evidencia queda registrada como un evento. Los eventos se encadenan: cada uno incluye la huella del anterior."
                />
                <div className="mt-10 rounded-2xl border border-border bg-elevated p-6">
                    <p className="text-sm text-text-muted">Cómo se encadenan</p>
                    <pre className="mt-4 overflow-x-auto font-mono text-sm leading-7 text-text">
                        {"H₁ = SHA-256(evento₁)\nH₂ = SHA-256(evento₂ + H₁)\nH₃ = SHA-256(evento₃ + H₂)"}
                    </pre>
                    <p className="mt-4 text-sm leading-6 text-text-muted">
                        Si alguien modificara un evento pasado, su huella cambiaría y dejaría
                        de coincidir con la que guarda el evento siguiente. La alteración
                        quedaría a la vista.
                    </p>
                </div>
            </div>

            <ol className="relative space-y-4 lg:pt-12">
                {EVENTS.map((event, index) => (
                    <li key={event.name} className="relative flex gap-5">
                        {index < EVENTS.length - 1 && (
                            <span
                                aria-hidden="true"
                                className="absolute top-10 -bottom-4 left-4 w-px -translate-x-1/2 bg-border-strong"
                            />
                        )}
                        <span
                            aria-hidden="true"
                            className="relative mt-5 flex size-8 shrink-0 items-center justify-center rounded-full border border-border-strong bg-elevated font-mono text-xs text-text-subtle"
                        >
                            {index + 1}
                        </span>
                        <div className="flex-1 rounded-2xl border border-border bg-card/60 p-5">
                            <div className="flex flex-wrap items-center justify-between gap-3">
                                <h3 className="font-medium">{event.name}</h3>
                                <StatusBadge tone={event.available ? "available" : "upcoming"} />
                            </div>
                            <p className="mt-2 text-sm leading-6 text-text-muted">{event.detail}</p>
                        </div>
                    </li>
                ))}
            </ol>
        </section>
    );
}