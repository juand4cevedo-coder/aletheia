/**
 * Huella SHA-256 de un archivo, en hexadecimal, calculada con Web Crypto.
 * Solo funciona en el navegador y en contextos seguros (HTTPS o localhost).
 */
export async function sha256File(file: File): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", await file.arrayBuffer());
  return Array.from(new Uint8Array(digest), (byte) =>
    byte.toString(16).padStart(2, "0"),
  ).join("");
}