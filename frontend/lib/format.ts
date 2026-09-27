const BYTE_UNITS = ["B", "KB", "MB", "GB"] as const;

/** Tamaño legible en unidades de 1024 bytes, con coma decimal (es-CO). */
export function formatBytes(bytes: number): string {
  let value = bytes;
  let unit = 0;
  while (value >= 1024 && unit < BYTE_UNITS.length - 1) {
    value /= 1024;
    unit += 1;
  }
  const digits = unit === 0 ? 0 : 1;
  return `${value.toLocaleString("es-CO", { maximumFractionDigits: digits })} ${BYTE_UNITS[unit]}`;
}

/** Divide una huella hexadecimal en grupos para leerla y cotejarla a simple vista. */
export function groupHash(hash: string, size = 8): string[] {
  const groups: string[] = [];
  for (let index = 0; index < hash.length; index += size) {
    groups.push(hash.slice(index, index + size));
  }
  return groups;
}