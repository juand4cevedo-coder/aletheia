import type { paths } from "./schema";

type Org = "/api/v1/organizations/{organization_id}";
type Json<T> = T extends { content: { "application/json": infer Body } } ? Body : never;

export type OrganizationSummary = Json<paths["/api/v1/organizations"]["get"]["responses"][200]>[number];
export type OrganizationDetail = Json<paths[Org]["get"]["responses"][200]>;
export type CaseSummary = Json<paths[`${Org}/cases`]["get"]["responses"][200]>[number];
export type CaseDetail = Json<paths[`${Org}/cases/{case_id}`]["get"]["responses"][200]>;
export type CaseMember = Json<paths[`${Org}/cases/{case_id}/members`]["get"]["responses"][200]>[number];
