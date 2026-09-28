import { SectionHeading } from "@/components/ui/section-heading";

const MEASURES = [
    {
        title: "Acceso por caso",
        body: "Pertenecer a la firma no da acceso a todos sus casos: hay que ser miembro de cada uno.",
    },
    {
        title: "Permisos en el servidor",
        body: "El servidor comprueba los permisos en cada petición. La interfaz nunca decide qué está permitido.",
    },
    {
        title: "Tipo real del archivo",
        body: "El tipo se detecta por el contenido. Un ejecutable renombrado como PDF se rechaza.",
    },
    {
        title: "Original inalterable",
        body: "El original preservado no puede sobrescribirse mediante las operaciones de la aplicación.",
    },
    {
        title: "Sesiones revocables",
        body: "Las sesiones son de corta duración y dejan de funcionar al instante al cerrar sesión.",
    },
    {
        title: "Contraseñas protegidas",
        body: "Se guardan con un algoritmo de derivación diseñado para contraseñas, nunca en texto plano.",
    },
] as const;

const COMMANDS = [
    { system: "Windows (PowerShell)", command: "Get-FileHash .\\acta.pdf -Algorithm SHA256" },
    { system: "macOS", command: "shasum -a 256 acta.pdf" },
    { system: "Linux", command: "sha256sum acta.pdf" },
] as const;

export function Trust() {
    return (
        <section
            aria-labelledby="confianza-title"
            id="confianza"
            className="mx-auto w-full max-w-6xl scroll-mt-20 px-6 py-24"
        >
            <SectionHeading
                id="confianza-title"
                eyebrow="Confianza"
                title="La confianza no se declara. Se construye con mecanismos verificables."
                intro="Estas son las medidas que ya funcionan. No prometemos seguridad absoluta: explicamos qué hacemos y cómo comprobarlo."
            />

            <ul className="mt-16 grid gap-x-10 gap-y-8 sm:grid-cols-2 lg:grid-cols-3">
                {MEASURES.map((measure) => (
                    <li key={measure.title} className="border-l-2 border-brand pl-5">
                        <h3 className="font-medium">{measure.title}</h3>
                        <p className="mt-2 text-sm leading-6 text-text-muted">{measure.body}</p>
                    </li>
                ))}
            </ul>

            <div className="mt-16 rounded-2xl border border-border bg-elevated p-6 sm:p-8">
                <h3 className="text-lg font-medium">Compruebe la huella sin depender de Aletheia</h3>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-text-muted">
                    SHA-256 es un estándar público. Cualquier persona puede recalcular la
                    huella de su copia con las herramientas del sistema operativo y
                    compararla con la registrada. Algunas herramientas la muestran en
                    mayúsculas: es la misma huella.
                </p>
                <dl className="mt-6 grid gap-3 lg:grid-cols-3">
                    {COMMANDS.map((item) => (
                        <div key={item.system} className="rounded-xl border border-border bg-background p-4">
                            <dt className="text-xs text-text-subtle">{item.system}</dt>
                            <dd className="mt-2 overflow-x-auto">
                                <code className="font-mono text-sm whitespace-pre">{item.command}</code>
                            </dd>
                        </div>
                    ))}
                </dl>
            </div>
        </section>
    );
}