/** Clases compartidas por todos los campos de formulario. */
export function inputStyles(invalid: boolean): string {
  return `block w-full rounded-lg border bg-background px-3.5 py-2.5 text-sm text-text placeholder:text-text-subtle transition-colors focus:outline-none focus-visible:outline-2 focus-visible:outline-offset-0 ${
    invalid
      ? "border-danger focus-visible:outline-danger"
      : "border-border-strong hover:border-text-subtle focus-visible:outline-accent"
  }`;
}