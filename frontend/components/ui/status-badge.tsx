type StatusBadgeProps = {
    tone: "available" | "upcoming";
};

const LABELS = {
    available: "Disponible",
    upcoming: "En desarrollo",
} as const;

/** Indica si una capacidad del producto ya funciona o está en desarrollo. */
export function StatusBadge({ tone }: StatusBadgeProps) {
    const available = tone === "available";

    return (
        <span
            className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs ${available
                    ? "border-success/40 text-success"
                    : "border-border-strong text-text-subtle"
                }`}
        >
            <span
                aria-hidden="true"
                className={`size-1.5 rounded-full ${available ? "bg-success" : "border border-text-subtle"}`}
            />
            {LABELS[tone]}
        </span>
    );
}