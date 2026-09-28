import Link from "next/link";

import { Logo } from "@/components/brand/logo";
import { IconChevronDown, IconLogout, IconMenu } from "@/components/ui/icons";
import { logout } from "@/features/auth/actions";
import type { OrganizationDetail, OrganizationSummary } from "@/lib/api/types";
import { organizationRoleLabel } from "@/lib/labels";

import { SidebarNav } from "./sidebar-nav";

type SidebarProps = {
  organization: OrganizationDetail;
  organizations: readonly OrganizationSummary[];
  user: { full_name: string; email: string };
};

function initials(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}

function OrganizationSwitcher({ organization, organizations }: Omit<SidebarProps, "user">) {
  const others = organizations.filter((item) => item.id !== organization.id);

  return (
    <details className="group relative">
      <summary className="flex cursor-pointer list-none items-center gap-3 rounded-xl border border-border bg-background/60 p-3 hover:border-border-strong [&::-webkit-details-marker]:hidden">
        <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-brand/25 text-sm font-semibold text-accent">
          {initials(organization.name)}
        </span>
        <span className="min-w-0 flex-1">
          <span className="block truncate text-sm font-medium">{organization.name}</span>
          <span className="block text-xs text-text-subtle">{organizationRoleLabel(organization.role)}</span>
        </span>
        <IconChevronDown className="size-4 text-text-subtle transition-transform group-open:rotate-180" />
      </summary>
      <div className="absolute inset-x-0 top-full z-20 mt-2 rounded-xl border border-border bg-elevated p-2 shadow-2xl shadow-black/40">
        <p className="px-2 py-1.5 text-xs text-text-subtle">
          {others.length > 0 ? "Cambiar de organización" : "No pertenece a otras organizaciones"}
        </p>
        {others.map((item) => (
          <Link
            key={item.id}
            href={`/app/${item.id}`}
            className="block rounded-lg px-2 py-2 text-sm text-text-muted hover:bg-card hover:text-text"
          >
            {item.name}
          </Link>
        ))}
      </div>
    </details>
  );
}

function SidebarContent({ organization, organizations, user }: SidebarProps) {
  return (
    <div className="flex h-full flex-col gap-6">
      <OrganizationSwitcher organization={organization} organizations={organizations} />
      <SidebarNav organizationId={organization.id} />
      <div className="mt-auto flex items-center gap-3 border-t border-border pt-4">
        <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-card text-xs font-semibold">
          {initials(user.full_name)}
        </span>
        <span className="min-w-0 flex-1">
          <span className="block truncate text-sm">{user.full_name}</span>
          <span className="block truncate text-xs text-text-subtle">{user.email}</span>
        </span>
        <form action={logout}>
          <button
            type="submit"
            aria-label="Cerrar sesión"
            title="Cerrar sesión"
            className="rounded-lg p-2 text-text-subtle hover:bg-card hover:text-text"
          >
            <IconLogout className="size-4" />
          </button>
        </form>
      </div>
    </div>
  );
}

/** Barra lateral en escritorio; menú desplegable en pantallas pequeñas. */
export function Sidebar(props: SidebarProps) {
  const home = `/app/${props.organization.id}`;

  return (
    <>
      <aside className="sticky top-0 hidden h-screen flex-col gap-8 border-r border-border bg-elevated px-4 py-6 lg:flex">
        <div className="px-2">
          <Logo href={home} />
        </div>
        <div className="min-h-0 flex-1">
          <SidebarContent {...props} />
        </div>
      </aside>

      <header className="sticky top-0 z-30 border-b border-border bg-elevated/95 backdrop-blur lg:hidden">
        <details className="group">
          <summary className="flex h-14 cursor-pointer list-none items-center justify-between px-5 [&::-webkit-details-marker]:hidden">
            <Logo href={home} />
            <span className="flex items-center gap-2 rounded-lg border border-border px-3 py-1.5 text-sm text-text-muted">
              <IconMenu className="size-4" />
              Menú
            </span>
          </summary>
          <div className="border-t border-border px-5 py-5">
            <SidebarContent {...props} />
          </div>
        </details>
      </header>
    </>
  );
}
