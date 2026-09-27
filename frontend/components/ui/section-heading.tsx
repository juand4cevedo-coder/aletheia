type SectionHeadingProps = {
    id: string;
    eyebrow: string;
    title: string;
    intro?: string;
    align?: "left" | "center";
};

/** Encabezado de sección de la landing: etiqueta, título y entradilla. */
export function SectionHeading({
    id,
    eyebrow,
    title,
    intro,
    align = "left",
}: SectionHeadingProps) {
    const centered = align === "center";

    return (
        <div className={centered ? "mx-auto max-w-3xl text-center" : "max-w-3xl"}>
            <p className="text-xs font-medium tracking-[0.18em] text-accent uppercase">
                {eyebrow}
            </p>
            <h2
                id={id}
                className="mt-4 text-4xl leading-[1.05] font-semibold tracking-tight text-balance sm:text-5xl"
            >
                {title}
            </h2>
            {intro && (
                <p
                    className={`mt-6 text-lg leading-8 text-text-muted ${centered ? "mx-auto max-w-2xl" : "max-w-2xl"}`}
                >
                    {intro}
                </p>
            )}
        </div>
    );
}