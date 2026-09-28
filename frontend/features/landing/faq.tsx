import { SectionHeading } from "@/components/ui/section-heading";

const QUESTIONS = [
    {
        question: "¿Qué hace Aletheia con una evidencia?",
        answer:
            "Guarda el archivo original sin posibilidad de sobrescritura, calcula su huella SHA-256 y registra quién lo incorporó, cuándo y en qué caso.",
    },
    {
        question: "¿Qué demuestra la huella SHA-256?",
        answer:
            "Que un contenido es idéntico, byte a byte, al que produjo la huella registrada. Si el archivo cambia en un solo byte, la huella es completamente distinta.",
    },
    {
        question: "¿Aletheia demuestra que una evidencia es auténtica?",
        answer:
            "No. Aletheia documenta qué archivo se incorporó y si su contenido sigue siendo el mismo. No determina si es auténtico, verdadero o admisible: esa valoración corresponde a la autoridad competente.",
    },
    {
        question: "¿Qué pasa si alguien modificó el archivo antes de subirlo?",
        answer:
            "Aletheia no puede saberlo. La huella documenta el contenido desde el momento de la preservación en adelante, no lo que ocurrió antes.",
    },
    {
        question: "¿Quién puede ver los casos de mi firma?",
        answer:
            "Solo las personas que son miembros de cada caso. Pertenecer a la organización no da acceso automático a todos sus casos.",
    },
    {
        question: "¿Qué archivos se pueden preservar?",
        answer:
            "Documentos, imágenes, audio, video y texto de hasta 100 MB. Los ejecutables y los archivos comprimidos se rechazan.",
    },
] as const;

export function Faq() {
    return (
        <section
            aria-labelledby="preguntas-title"
            id="preguntas"
            className="mx-auto grid w-full max-w-6xl scroll-mt-20 gap-12 px-6 py-24 lg:grid-cols-[1fr_1.4fr]"
        >
            <SectionHeading
                id="preguntas-title"
                eyebrow="Preguntas frecuentes"
                title="Lo que Aletheia hace, y lo que no pretende demostrar."
            />

            <div className="divide-y divide-border border-y border-border">
                {QUESTIONS.map((item) => (
                    <details key={item.question} className="group">
                        <summary className="flex cursor-pointer list-none items-center justify-between gap-6 py-5 font-medium [&::-webkit-details-marker]:hidden">
                            {item.question}
                            <span
                                aria-hidden="true"
                                className="flex size-7 shrink-0 items-center justify-center rounded-full border border-border-strong text-text-muted transition-transform group-open:rotate-45"
                            >
                                +
                            </span>
                        </summary>
                        <p className="pb-6 leading-7 text-text-muted">{item.answer}</p>
                    </details>
                ))}
            </div>
        </section>
    );
}