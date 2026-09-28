import type { Metadata } from "next";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { IconChevronRight, IconFolder, IconShield, IconUsers } from "@/components/ui/icons";
import { NewCaseDialog } from "@/features/cases/new-case-dialog";
import { getOrganization, listCases } from "@/features/workspace/data";
import { requireUser } from "@/lib/auth/dal";
import { formatDate } from "@/lib/format";
import { can, caseRoleLabel, organizationRoleLabel } from "@/lib/labels";

export const metadata: Metadata = {
  title: "Inicio",
};

export default async function WorkspaceHomePage({ params }: PageProps<"/app/[orgId]">) {
  const { orgId } = await params;
  const [user, organization, cases] = await Promise.all([
    requireUser(),
    getOrganization(orgId),
    listCases(orgId),
  ]);

  const firstName = user.full_name.split(/\s+/)[0] ?? user.full_name;
  const canCreate = can(organization.permissions, "case:create");
  const activeCases = cases.filter((item) => item.status.toLowerCase() === "active").length;
  const leading = cases.filter((item) => item.my_role === "lead").length;
  const recent = [...cases].sort((a, b) => b.created_at.localeCompare(a.created_at)).slice(0, 5);

  const stats = [
    { label: "Casos activos", value: activeCases, icon: IconFolder },
    { label: "Casos que usted dirige", value: leading, icon: IconShield },
    { label: "Su rol en la organización", value: organizationRoleLabel(organization.role), icon: IconUsers },
  ];

  return (
    <main className="mx-auto w-full max-w-5xl px-5 py-10 sm:px-8 lg:py-14">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm text-text-subtle">{organization.name}</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight">Hola, {firstName}</h1>
        </div>
        {canCreate && <NewCaseDialog organizationId={orgId} />}
      </div>

      <dl className="mt-10 grid gap-4 sm:grid-cols-3">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-2xl border border-border bg-card/60 p-5">
            <dt className="flex items-center gap-2 text-sm text-text-muted">
              <stat.icon className="size-4 text-accent" />
              {stat.label}
            </dt>
            <dd className="mt-3 text-3xl font-semibold tracking-tight">{stat.value}</dd>
          </div>
        ))}
      </dl>

      {cases.length === 0 ? (
        <section aria-labelledby="first-steps" className="mt-10 rounded-2xl border border-border bg-elevated p-6 sm:p-8">
          <h2 id="first-steps" className="text-lg font-semibold">
            Primeros pasos
          </h2>
          <ol className="mt-6 space-y-5">
            {[
              { title: "Cree su primer caso", body: "El caso reúne a las personas autorizadas y la evidencia de un mismo asunto." },
              { title: "Incorpore una evidencia", body: "Suba el archivo original: Aletheia calcula su huella SHA-256 y lo preserva." },
              { title: "Compruebe una copia", body: "Compare cualquier copia con la huella registrada para saber si es idéntica." },
            ].map((step, index) => (
              <li key={step.title} className="flex gap-4">
                <span className="flex size-8 shrink-0 items-center justify-center rounded-full border border-border-strong font-mono text-xs text-text-subtle">
                  {index + 1}
                </span>
                <div>
                  <p className="font-medium">{step.title}</p>
                  <p className="mt-1 text-sm text-text-muted">{step.body}</p>
                </div>
              </li>
            ))}
          </ol>
          {canCreate ? (
            <div className="mt-8">
              <NewCaseDialog organizationId={orgId} />
            </div>
          ) : (
            <p className="mt-8 text-sm text-text-muted">
              Su rol no permite crear casos. Cuando un responsable le añada a uno, aparecerá aquí.
            </p>
          )}
        </section>
      ) : (
        <section aria-labelledby="recent-cases" className="mt-10">
          <div className="flex items-center justify-between gap-4">
            <h2 id="recent-cases" className="text-lg font-semibold">
              Casos recientes
            </h2>
            <Link href={`/app/${orgId}/cases`} className="text-sm text-accent hover:underline">
              Ver todos
            </Link>
          </div>
          <ul className="mt-4 divide-y divide-border overflow-hidden rounded-2xl border border-border bg-card/40">
            {recent.map((item) => (
              <li key={item.id}>
                <Link
                  href={`/app/${orgId}/cases/${item.id}`}
                  className="group flex items-center gap-4 p-5 transition-colors hover:bg-card"
                >
                  <div className="min-w-0 flex-1">
                    <span className="font-mono text-xs text-accent">{item.reference}</span>
                    <p className="mt-1 truncate font-medium">{item.title}</p>
                  </div>
                  <div className="hidden shrink-0 text-right sm:block">
                    <Badge tone={item.my_role === "lead" ? "accent" : "neutral"}>{caseRoleLabel(item.my_role)}</Badge>
                    <p className="mt-2 text-xs text-text-subtle">{formatDate(item.created_at)}</p>
                  </div>
                  <IconChevronRight className="size-4 shrink-0 text-text-subtle transition-transform group-hover:translate-x-0.5" />
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
