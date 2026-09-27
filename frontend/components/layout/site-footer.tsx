import Link from "next/link";

import { Logo } from "@/components/brand/logo";

import { MARKETING_SECTIONS } from "./marketing-nav";

export function SiteFooter() {
    return (
        <footer className="border-t border-border bg-elevated">
            <div className="mx-auto grid w-full max-w-6xl gap-12 px-6 py-14 md:grid-cols-[2fr_1fr_1fr]">
                <div>
                    <Logo />
                    <p className="mt-5 max-w-sm text-sm leading-6 text-text-muted">
                        Preservación, trazabilidad e integridad de evidencia digital para
                        abogados y firmas en Colombia.
                    </p>
                </div>

                <nav aria-labelledby="footer-producto">
                    <h2 id="footer-producto" className="text-sm font-medium">
                        Producto
                    </h2>
                    <ul className="mt-4 space-y-3 text-sm text-text-muted">
                        {MARKETING_SECTIONS.map((section) => (
                            <li key={section.href}>
                                <Link href={section.href} className="hover:text-text">
                                    {section.label}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </nav>

                <nav aria-labelledby="footer-cuenta">
                    <h2 id="footer-cuenta" className="text-sm font-medium">
                        Cuenta
                    </h2>
                    <ul className="mt-4 space-y-3 text-sm text-text-muted">
                        <li>
                            <Link href="/login" className="hover:text-text">
                                Iniciar sesión
                            </Link>
                        </li>
                        <li>
                            <Link href="/register" className="hover:text-text">
                                Crear cuenta
                            </Link>
                        </li>
                    </ul>
                </nav>
            </div>

            <div className="border-t border-border">
                <p className="mx-auto w-full max-w-6xl px-6 py-6 text-xs leading-5 text-text-subtle">
                    Aletheia documenta los registros y verificaciones que efectúa sobre la
                    evidencia incorporada a la plataforma. No determina la autenticidad,
                    admisibilidad, suficiencia ni valor probatorio de una evidencia: esa
                    valoración corresponde a la autoridad competente conforme al marco
                    jurídico aplicable.
                </p>
            </div>
        </footer>
    );
}