import { StatusBadge } from "@/components/ui/status-badge";

import { PLANS } from "./plans";

type Row = {
    label: string;
    values: readonly string[] | "all" | "upcoming";
};

const ROWS: readonly Row[] = [
    { label: "Usuarios", values: PLANS.map((plan) => (plan.maxUsers === null ? "A medida" : plan.maxUsers === 1 ? "1" : `Hasta ${plan.maxUsers}`)) },
    { label: "Casos activos", values: PLANS.map((plan) => plan.activeCases) },
    { label: "Almacenamiento", values: PLANS.map((plan) => plan.storage) },
    { label: "Tamaño máximo por archivo", values: PLANS.map(() => "100 MB") },
    { label: "Huella SHA-256 y original sin sobrescritura", values: "all" },
    { label: "Detección del tipo real del archivo", values: "all" },
    { label: "Miembros y roles por caso", values: "all" },
    { label: "Historial encadenado de eventos", values: "upcoming" },
    { label: "Verificación de integridad bajo demanda", values: "upcoming" },
    { label: "Informes de preservación", values: "upcoming" },
    { label: "Soporte", values: PLANS.map((plan) => plan.support) },
];

function Cell({ row, index }: { row: Row; index: number }) {
    if (row.values === "all") {
        return (
            <span className="inline-flex items-center gap-2 text-success">
                <svg aria-hidden="true" viewBox="0 0 16 16" className="size-4" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="m3.5 8.5 3 3 6-7" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <span className="sr-only">Incluido</span>
            </span>
        );
    }
    if (row.values === "upcoming") {
        return <StatusBadge tone="upcoming" />;
    }
    return <span className="text-text-muted">{row.values[index]}</span>;
}

/** Tabla completa de los planes, desplegable para no saturar la sección. */
export function PricingComparison() {
    return (
        <details className="group mt-8 rounded-2xl border border-border">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 p-6 font-medium [&::-webkit-details-marker]:hidden">
                Comparar todos los detalles
                <span
                    aria-hidden="true"
                    className="flex size-7 shrink-0 items-center justify-center rounded-full border border-border-strong text-text-muted transition-transform group-open:rotate-45"
                >
                    +
                </span>
            </summary>

            <div className="overflow-x-auto border-t border-border">
                <table className="w-full min-w-[44rem] text-left text-sm">
                    <caption className="sr-only">Comparación de los planes de Aletheia</caption>
                    <thead>
                        <tr className="border-b border-border">
                            <th scope="col" className="sticky left-0 bg-background p-4 font-medium text-text-subtle">
                                Característica
                            </th>
                            {PLANS.map((plan) => (
                                <th key={plan.id} scope="col" className="p-4 font-semibold">
                                    {plan.name}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                        {ROWS.map((row) => (
                            <tr key={row.label}>
                                <th scope="row" className="sticky left-0 bg-background p-4 font-normal">
                                    {row.label}
                                </th>
                                {PLANS.map((plan, index) => (
                                    <td key={plan.id} className="p-4">
                                        <Cell row={row} index={index} />
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </details>
    );
}