import Image from "next/image";
import Link from "next/link";

type LogoProps = {
    href?: string;
};

/** Símbolo y nombre de Aletheia. El nombre replica el espaciado del logotipo. */
export function Logo({ href = "/" }: LogoProps) {
    return (
        <Link
            href={href}
            aria-label="Aletheia, inicio"
            className="inline-flex items-center gap-3 rounded-md"
        >
            <Image src="/brand/aletheia-mark.png" alt="" width={30} height={28} priority />
            <span className="text-sm font-semibold tracking-[0.2em] text-text sm:tracking-[0.3em]">ALETHEIA</span>
        </Link>
    );
}