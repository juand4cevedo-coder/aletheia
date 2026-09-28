/** Textos en español para los valores que devuelve la API. */

const ORGANIZATION_ROLES: Record<string, string> = {
  owner: "Propietario",
  admin: "Administrador",
  lawyer: "Abogado",
  collaborator: "Colaborador",
  auditor: "Auditor",
};

const CASE_ROLES: Record<string, string> = {
  lead: "Responsable",
  editor: "Editor",
  viewer: "Lector",
};

const CASE_STATUSES: Record<string, string> = {
  active: "Activo",
  closed: "Cerrado",
  archived: "Archivado",
  under_legal_hold: "Conservación obligatoria",
  pending_deletion: "Pendiente de eliminación",
  deleted: "Eliminado",
};

export function organizationRoleLabel(role: string): string {
  return ORGANIZATION_ROLES[role] ?? role;
}

export function caseRoleLabel(role: string): string {
  return CASE_ROLES[role] ?? role;
}

export function caseStatusLabel(status: string): string {
  return CASE_STATUSES[status.toLowerCase()] ?? status;
}

/** El frontend solo muestra u oculta acciones; la API decide si se permiten. */
export function can(permissions: readonly string[], permission: string): boolean {
  return permissions.includes(permission);
}
