export type PlanId = "individual" | "firma" | "profesional" | "enterprise";

export type Plan = {
  id: PlanId;
  name: string;
  audience: string;
  /** Precio mensual en pesos colombianos; `null` si es a medida. */
  monthlyPrice: number | null;
  /** Máximo de usuarios; `null` si no tiene límite fijo. */
  maxUsers: number | null;
  activeCases: string;
  storage: string;
  support: string;
  highlights: readonly string[];
};

/** Meses que se cobran al pagar un año completo (12 - meses sin costo). */
export const ANNUAL_BILLED_MONTHS = 10;

/** Dirección para solicitar el plan Enterprise. Confirmar que existe. */
export const SALES_EMAIL = "contacto@aletheia.sbs";

export const PLANS: readonly Plan[] = [
  {
    id: "individual",
    name: "Individual",
    audience: "Para abogados independientes que preservan evidencia de sus propios casos.",
    monthlyPrice: 59_900,
    maxUsers: 1,
    activeCases: "25",
    storage: "20 GB",
    support: "Correo",
    highlights: ["1 usuario", "25 casos activos", "20 GB de almacenamiento", "Huella SHA-256 de cada archivo"],
  },
  {
    id: "firma",
    name: "Firma",
    audience: "Para equipos pequeños que trabajan sobre los mismos casos.",
    monthlyPrice: 149_900,
    maxUsers: 5,
    activeCases: "150",
    storage: "100 GB",
    support: "Correo prioritario",
    highlights: ["Hasta 5 usuarios", "150 casos activos", "100 GB de almacenamiento", "Roles por caso"],
  },
  {
    id: "profesional",
    name: "Profesional",
    audience: "Para firmas con más personas, más casos y más volumen de evidencia.",
    monthlyPrice: 299_900,
    maxUsers: 15,
    activeCases: "Ilimitados",
    storage: "500 GB",
    support: "Correo prioritario y acompañamiento inicial",
    highlights: ["Hasta 15 usuarios", "Casos ilimitados", "500 GB de almacenamiento", "Acompañamiento inicial"],
  },
  {
    id: "enterprise",
    name: "Enterprise",
    audience: "Para organizaciones con necesidades específicas de capacidad u operación.",
    monthlyPrice: null,
    maxUsers: null,
    activeCases: "A medida",
    storage: "A medida",
    support: "Condiciones acordadas",
    highlights: ["Más de 15 usuarios", "Capacidad a medida", "Incorporación asistida", "Condiciones acordadas"],
  },
];

/** Plan recomendado según el número de personas que usarán Aletheia. */
export function recommendPlan(users: number): PlanId {
  const fit = PLANS.find((plan) => plan.maxUsers !== null && users <= plan.maxUsers);
  return fit?.id ?? "enterprise";
}

const COP = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  maximumFractionDigits: 0,
});

export function formatCop(value: number): string {
  return COP.format(value);
}