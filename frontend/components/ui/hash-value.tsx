import { groupHash } from "@/lib/format";

type HashValueProps = {
    value: string;
    className?: string;
};

/**
 * Huella SHA-256 en grupos de 8 caracteres.
 * La separación es solo visual: al seleccionar y copiar, la huella sale continua.
 */
export function HashValue({ value, className = "" }: HashValueProps) {
    return (
        <code
            className={`flex flex-wrap gap-x-2 gap-y-1 font-mono text-sm leading-6 break-all ${className}`}
        >
            {groupHash(value).map((group, index) => (
                <span key={index}>{group}</span>
            ))}
        </code>
    );
}