type ButtonVariant = "primary" | "secondary" | "ghost";
type ButtonSize = "md" | "lg";

const BASE =
  "inline-flex items-center justify-center gap-2 rounded-lg font-medium whitespace-nowrap transition-colors disabled:cursor-not-allowed disabled:opacity-60";

const VARIANTS: Record<ButtonVariant, string> = {
  primary: "bg-accent text-on-accent hover:bg-text",
  secondary: "border border-border-strong text-text hover:border-accent",
  ghost: "text-text-muted hover:text-text",
};

const SIZES: Record<ButtonSize, string> = {
  md: "px-4 py-2 text-sm",
  lg: "px-5 py-3 text-sm",
};

/**
 * Clases de botón compartidas por `<button>` y `<Link>`, para que un enlace
 * con aspecto de botón y un botón real se vean exactamente igual.
 */
export function buttonStyles(
  variant: ButtonVariant = "primary",
  size: ButtonSize = "md",
): string {
  return `${BASE} ${VARIANTS[variant]} ${SIZES[size]}`;
}