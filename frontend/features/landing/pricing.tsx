import { SectionHeading } from "@/components/ui/section-heading";

import { PricingComparison } from "./pricing-comparison";
import { PricingExplorer } from "./pricing-explorer";

export function Pricing() {
    return (
        <section
            aria-labelledby="planes-title"
            id="planes"
            className="mx-auto w-full max-w-6xl scroll-mt-20 px-6 py-24"
        >
            <SectionHeading
                id="planes-title"
                eyebrow="Planes"
                title="La capacidad que su práctica necesita, sin perder el control."
                intro="Todos los planes preservan la evidencia de la misma forma. Cambian las personas, los casos y el almacenamiento."
                align="center"
            />

            <div className="mt-16">
                <PricingExplorer />
            </div>

            <PricingComparison />

            <p className="mx-auto mt-8 max-w-3xl text-center text-sm leading-6 text-text-subtle">
                Precios de referencia en pesos colombianos. La facturación todavía no
                está habilitada: durante esta etapa las cuentas se crean sin cobro.
            </p>
        </section>
    );
}