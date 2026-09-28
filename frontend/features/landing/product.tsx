import { SectionHeading } from "@/components/ui/section-heading";
import { StatusBadge } from "@/components/ui/status-badge";

const MODULES = [
    {
        name: "Casos",
        summary: "Cada evidencia pertenece a un caso, que reúne a las personas autorizadas y todo lo preservado.",
        features: ["Referencia única por caso", "Miembros con rol propio", "Acceso solo para miembros"],
        available: true,
    },
    {
        name: "Evidencia",
        summary: "El archivo original junto con su huella, su tipo real y el registro de quién lo incorporó y cuándo.",
        features: ["Huella SHA-256", "Original sin sobrescritura", "Tipo detectado por contenido"],
        available: true,
    },
    {
        name: "Verificación",
        summary: "Volver a calcular la huella del archivo almacenado y compararla con la registrada al preservarlo.",
        features: ["Huella registrada y actual", "Resultado documentado", "Evento en el historial"],
        available: false,
    },
    {
        name: "Informes",
        summary: "Un documento con el registro de preservación, la huella y los eventos relevantes de una evidencia.",
        features: ["Datos de preservación", "Estado de integridad", "Eventos relevantes"],
        available: false,
    },
] as const;

export function Product() {
    return (
        <section
            aria-labelledby="producto-title"
            id="producto"
            className="mx-auto w-full max-w-6xl scroll-mt-20 px-6 py-24"
        >
            <SectionHeading
                id="producto-title"
                eyebrow="El producto"
                title="Todo lo necesario para saber qué ocurrió con una evidencia."
                intro="Aletheia organiza casos, evidencia, verificaciones e informes alrededor de un mismo registro técnico."
            />

            <div className="mt-16 grid gap-4 md:grid-cols-2">
                {MODULES.map((module) => (
                    <article
                        key={module.name}
                        className="flex flex-col rounded-2xl border border-border bg-card/60 p-6 sm:p-8"
                    >
                        <div className="flex flex-wrap items-center justify-between gap-3">
                            <h3 className="text-xl font-semibold">{module.name}</h3>
                            <StatusBadge tone={module.available ? "available" : "upcoming"} />
                        </div>
                        <p className="mt-3 leading-7 text-text-muted">{module.summary}</p>
                        <ul className="mt-6 space-y-2 border-t border-border pt-6 text-sm text-text-muted">
                            {module.features.map((feature) => (
                                <li key={feature} className="flex items-center gap-3">
                                    <span aria-hidden="true" className="size-1.5 shrink-0 rounded-full bg-accent" />
                                    {feature}
                                </li>
                            ))}
                        </ul>
                    </article>
                ))}
            </div>
        </section>
    );
}