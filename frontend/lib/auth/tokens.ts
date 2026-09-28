import type { paths } from "@/lib/api/schema";

/** Par de tokens que devuelven el login y el refresh de la API. */
export type TokenPair =
  paths["/api/v1/auth/login"]["post"]["responses"][200]["content"]["application/json"];