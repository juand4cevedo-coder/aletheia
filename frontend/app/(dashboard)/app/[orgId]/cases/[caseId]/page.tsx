import type { Metadata } from "next";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { IconChevronRight } from "@/components/ui/icons";
import { CaseEditor } from "@/features/cases/case-editor";
import { getCase, listCaseMembers } from "@/features/workspace/data";
import { formatDate, formatDateTime } from "@/lib/format";
import { can, caseRoleLabel, caseStatusLabel } from "@/lib/labels";

export async function generateMetadata({ params }: PageProps<"/app/[orgId]/cases/[caseId]">): Promise<Metadata> {
  const { orgId, caseId } = await params;
  const item = await getCase(orgId, caseId);
  return { title: `${item.reference} · ${item.title}` };
}

const CAPABILITIES = [
  { permission: "case:update", label: "Editar los datos del caso" },
  { permission: "case:manage_members", label: "Gestionar los miembros" },
  { permission: "evidence:create", label: "Incorporar evidencia" },
  { permission: "evidence:read", label: "Consultar la evidencia" },
] as const;

export default async function CasePage({ params }: PageProps<"/app/[orgId]/cases/[caseId]">) {
  const { orgId, caseId } = await params;
  const [item, members] = await Promise.all([getCase(orgId, caseId), listCaseMembers(orgId, caseId)]);
  const active = item.status.toLowerCase() === "active";

  return (
    <main className="mx-auto w-full max-w-5xl px-5 py-10 sm:px-8 lg:py-14">
      <nav aria-label="Ruta" className="flex items-center gap-2 text-sm text-text-subtle">
        <Link href={`/app/${orgId}/cases`} className="hover:text-text">
          Casos
        </Link>
        <IconChevronRight className="size-3.5" />
        <span aria-current="page" className="font-mono text-text-muted">
          {item.reference}
        </span>
      </nav>

      <div className="mt-6 flex flex-wrap items-center gap-2">
        <span className="rounded-md border border-accent/40 bg-accent/10 px-2 py-0.5 font-mono text-xs text-accent">
          {item.reference}
        </span>
        <Badge tone={active ? "success" : "neutral"}>{caseStatusLabel(item.status)}</Badge>
        <Badge tone={item.my_role === "lead" ? "accent" : "neutral"}>Su rol: {caseRoleLabel(item.my_role)}</Badge>
      </div>

      <div className="mt-5">
        {can(item.my_permissions, "case:update") ? (
          <CaseEditor
            organizationId={orgId}
            caseId={caseId}
            title={item.title}
            description={item.description ?? null}
          />
        ) : (
          <>
            <h1 className="text-3xl leading-tight font-semibold tracking-tight text-balance sm:text-4xl">{item.title}</h1>
            {item.description && (
              <p className="mt-4 max-w-3xl leading-7 whitespace-pre-line text-text-muted">{item.description}</p>
            )}
          </>
        )}
      </div>

      <div className="mt-12 grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        <section aria-labelledby="members-title" className="rounded-2xl border border-border bg-card/40">
          <div className="flex items-center justify-between gap-4 border-b border-border p-5">
            <h2 id="members-title" className="font-semibold">
              Miembros
            </h2>
            <span className="text-sm text-text-subtle">{members.length}</span>
          </div>
          <ul className="divide-y divide-border">
            {members.map((member) => (
              <li key={member.user_id} className="flex items-center gap-4 p-5">
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium">{member.full_name}</p>
                  <p className="truncate text-sm text-text-muted">{member.email}</p>
                </div>
                <div className="shrink-0 text-right">
                  <Badge tone={member.role === "lead" ? "accent" : "neutral"}>{caseRoleLabel(member.role)}</Badge>
                  <p className="mt-2 text-xs text-text-subtle">Desde {formatDate(member.added_at)}</p>
                </div>
              </li>
            ))}
          </ul>
        </section>

        <aside className="space-y-6">
          <section aria-labelledby="capabilities-title" className="rounded-2xl border border-border bg-card/40 p-5">
            <h2 id="capabilities-title" className="font-semibold">
              Lo que usted puede hacer
            </h2>
            <ul className="mt-4 space-y-3 text-sm">
              {CAPABILITIES.map((capability) => {
                const allowed = can(item.my_permissions, capability.permission);
                return (
                  <li key={capability.permission} className={`flex items-center gap-3 ${allowed ? "" : "text-text-subtle"}`}>
                    <span
                      aria-hidden="true"
                      className={`size-2 shrink-0 rounded-full ${allowed ? "bg-success" : "border border-text-subtle"}`}
                    />
                    <span>
                      {capability.label}
                      <span className="sr-only">{allowed ? ": permitido" : ": no permitido"}</span>
                    </span>
                  </li>
                );
              })}
            </ul>
          </section>

          <section className="rounded-2xl border border-border bg-card/40 p-5 text-sm">
            <dl className="space-y-3">
              <div className="flex justify-between gap-4">
                <dt className="text-text-muted">Creado</dt>
                <dd>{formatDateTime(item.created_at)}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-text-muted">Estado</dt>
                <dd>{caseStatusLabel(item.status)}</dd>
              </div>
            </dl>
          </section>
        </aside>
      </div>
    </main>
  );
}
