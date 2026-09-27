import Link from "next/link";

import { Logo } from "@/components/brand/logo";
import { buttonStyles } from "@/components/ui/button-styles";

import { MARKETING_SECTIONS } from "./marketing-nav";

export function SiteHeader() {
    return (
        <header className="sticky top-0 z-40 border-b border-border/60 bg-background/85 backdrop-blur">
            <div className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between gap-3 px-5 sm:gap-6 sm:px-6">
                <Logo />

                <nav aria-label="Secciones" className="hidden lg:block">
                    <ul className="flex items-center gap-8 text-sm text-text-muted">
                        {MARKETING_SECTIONS.map((section) => (
                            <li key={section.href}>
                                <Link href={section.href} className="rounded-sm hover:text-text">
                                    {section.label}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </nav>

                <div className="flex items-center gap-2">
                    <Link href="/login" className={buttonStyles("ghost")}>
                        Iniciar sesión
                    </Link>
                    <span className="hidden sm:block">
                        <Link href="/register" className={buttonStyles("secondary")}>
                            Crear cuenta
                        </Link>
                    </span>
                </div>
            </div>
        </header>
    );
}