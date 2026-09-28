import "server-only";

import { notFound } from "next/navigation";
import { cache } from "react";

import { getApiClient, unwrap } from "@/lib/api/client";
import { ApiError } from "@/lib/api/errors";
import { requireAccessToken } from "@/lib/auth/dal";
import { bearer } from "@/lib/auth/session";

/** Un 404 de la API (no existe o no hay acceso) se muestra como página no encontrada. */
async function orNotFound<T>(request: Promise<T>): Promise<T> {
  try {
    return await request;
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }
}

async function auth() {
  return { headers: bearer(await requireAccessToken()) };
}

export const listOrganizations = cache(async () =>
  unwrap(getApiClient().GET("/api/v1/organizations", await auth())),
);

export const getOrganization = cache(async (organizationId: string) =>
  orNotFound(
    unwrap(
      getApiClient().GET("/api/v1/organizations/{organization_id}", {
        ...(await auth()),
        params: { path: { organization_id: organizationId } },
      }),
    ),
  ),
);

export const listCases = cache(async (organizationId: string) =>
  orNotFound(
    unwrap(
      getApiClient().GET("/api/v1/organizations/{organization_id}/cases", {
        ...(await auth()),
        params: { path: { organization_id: organizationId } },
      }),
    ),
  ),
);

export const getCase = cache(async (organizationId: string, caseId: string) =>
  orNotFound(
    unwrap(
      getApiClient().GET("/api/v1/organizations/{organization_id}/cases/{case_id}", {
        ...(await auth()),
        params: { path: { organization_id: organizationId, case_id: caseId } },
      }),
    ),
  ),
);

export const listCaseMembers = cache(async (organizationId: string, caseId: string) =>
  orNotFound(
    unwrap(
      getApiClient().GET("/api/v1/organizations/{organization_id}/cases/{case_id}/members", {
        ...(await auth()),
        params: { path: { organization_id: organizationId, case_id: caseId } },
      }),
    ),
  ),
);
