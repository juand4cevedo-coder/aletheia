import { SectionHeading } from "@/components/ui/section-heading";

const STEPS = [
    { name: "Carga", detail: "Un miembro del caso sube el archivo original." },
    { name: "Validación", detail: "Se detecta el tipo real por su contenido, no por la extensión." },
    { name: "Huella SHA-256", detail: "Se calcula sobre cada byte del archivo." },
    { name: "Almacenamiento", detail: "El original se guarda sin posibilidad de sobrescritura." },
    { name: "Registro", detail: "Queda asociado al caso, con fecha, hora y usuario." },
] as const;

const FORMATS = [
    { group: "Documentos", extensions: "PDF, DOCX, XLSX, PPTX" },
    { group: "Imágenes", extensions: "JPG, PNG, GIF, WEBP, HEIC, TIFF" },
    { group: "Audio", extensions: "MP3, M4A, OGG, OPUS, WAV, AAC, AMR" },
    { group: "Video", extensions: "MP4, MOV, WEBM, 3GP" },
    { group: "Texto", extensions: "TXT, CSV, EML" },
] as const;

export function Preservation() {
    return (
        <section
            aria-labelledby="como-funciona-title"
            id="como-funciona"
            className="mx-auto w-full max-w-6xl scroll-mt-20 px-6 py-24"
        >
            <SectionHeading
                id="como-funciona-title"
                eyebrow="Preservación"
                title="La preservación convierte un archivo en un registro documentado."
                intro="Cada evidencia recorre el mismo proceso al incorporarse. El resultado es un original intacto y un registro de qué se preservó, cuándo y por quién."
                align="center"
            />

            <div className="mt-16 rounded-2xl border border-border bg-card/60 p-6 sm:p-10">
                <ol className="grid gap-8 md:grid-cols-5 md:gap-6">
                    {STEPS.map((step, index) => (
                        <li key={step.name} className="relative">
                            {index < STEPS.length - 1 && (
                                <span
                                    aria-hidden="true"
                                    className="absolute top-4 left-10 hidden h-px w-[calc(100%-1rem)] bg-border-strong md:block"
                                />
                            )}
                            <span
                                aria-hidden="true"
                                className="relative flex size-8 items-center justify-center rounded-full border border-accent/60 bg-elevated font-mono text-xs text-accent"
                            >
                                {index + 1}
                            </span>
                            <h3 className="mt-5 font-medium">{step.name}</h3>
                            <p className="mt-2 text-sm leading-6 text-text-muted">{step.detail}</p>
                        </li>
                    ))}
                </ol>
            </div>

            <div className="mt-8 grid gap-6 rounded-2xl border border-border p-6 sm:p-8 lg:grid-cols-[14rem_1fr]">
                <div>
                    <h3 className="font-medium">Formatos admitidos</h3>
                    <p className="mt-2 text-sm leading-6 text-text-muted">
                        Hasta 100 MB por archivo. Ejecutables y archivos comprimidos se rechazan.
                    </p>
                </div>
                <dl className="grid gap-x-8 gap-y-4 sm:grid-cols-2 lg:grid-cols-3">
                    {FORMATS.map((format) => (
                        <div key={format.group}>
                            <dt className="text-sm font-medium">{format.group}</dt>
                            <dd className="mt-1 text-sm text-text-muted">{format.extensions}</dd>
                        </div>
                    ))}
                </dl>
            </div>
        </section>
    );
}