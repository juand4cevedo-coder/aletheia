import type { Metadata } from "next";

import { CaseList } from "@/features/cases/case-list";
import { NewCaseDialog } from "@/features/cases/new-case-dialog";
import { getOrganization, listCases } from "@/features/workspace/data";
import { can } from "@/lib/labels";

export const metadata: Metadata = {
  title: "Casos",
};

export default async function CasesPage({ params }: PageProps<"/app/[orgId]/cases">) {
  const { orgId } = await params;
  const [organization, cases] = await Promise.all([getOrganization(orgId), listCases(orgId)]);
  const canCreate = can(organization.permissions, "case:create");

  return (
    <main className="mx-auto w-full max-w-5xl px-5 py-10 sm:px-8 lg:py-14">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Casos</h1>
          <p className="mt-2 text-text-muted">Los casos de {organization.name} en los que usted participa.</p>
        </div>
        {canCreate && <NewCaseDialog organizationId={orgId} />}
      </div>

      <div className="mt-10">
        {cases.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-border-strong p-12 text-center">
            <p className="text-lg font-medium">Todavía no participa en ningún caso.</p>
            <p className="mx-auto mt-2 max-w-md text-sm text-text-muted">
              {canCreate
                ? "Cree el primero para empezar a preservar evidencia."
                : "Cuando un responsable le añada a un caso, aparecerá aquí."}
            </p>
            {canCreate && (
              <div className="mt-6 flex justify-center">
                <NewCaseDialog organizationId={orgId} />
              </div>
            )}
          </div>
        ) : (
          <CaseList organizationId={orgId} cases={cases} />
        )}
      </div>
    </main>
  );
}
