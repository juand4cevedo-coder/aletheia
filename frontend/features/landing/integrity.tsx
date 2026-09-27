import { SectionHeading } from "@/components/ui/section-heading";

import { IntegrityDemo } from "./integrity-demo";

export function Integrity() {
    return (
        <section
            aria-labelledby="integridad-title"
            id="integridad"
            className="mx-auto w-full max-w-6xl scroll-mt-20 px-6 py-24"
        >
            <SectionHeading
                id="integridad-title"
                eyebrow="Integridad"
                title="Una huella permite comprobar si el contenido es el mismo."
                intro="Verificar una evidencia es calcular de nuevo su huella SHA-256 y compararla con la registrada al preservarla. Pruébelo aquí con dos archivos."
                align="center"
            />

            <div className="mt-16">
                <IntegrityDemo />
            </div>

            <p className="mx-auto mt-8 max-w-3xl text-center text-sm leading-6 text-text-subtle">
                Una coincidencia documenta que el contenido no ha cambiado desde que se
                registró su huella. No determina por sí sola la autenticidad,
                admisibilidad ni valor probatorio de la evidencia.
            </p>
        </section>
    );
}