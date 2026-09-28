"use client";

import Link from "next/link";
import { useDeferredValue, useEffect, useId, useMemo, useRef, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { IconChevronRight, IconSearch } from "@/components/ui/icons";
import type { CaseSummary } from "@/lib/api/types";
import { formatDate } from "@/lib/format";
import { caseRoleLabel, caseStatusLabel } from "@/lib/labels";

type RoleFilter = "all" | "lead" | "editor" | "viewer";
type Sort = "recent" | "title";

const ROLE_FILTERS: readonly { value: RoleFilter; label: string }[] = [
  { value: "all", label: "Todos" },
  { value: "lead", label: "Responsable" },
  { value: "editor", label: "Editor" },
  { value: "viewer", label: "Lector" },
];

function normalize(value: string): string {
  return value.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase();
}

type CaseListProps = {
  organizationId: string;
  cases: readonly CaseSummary[];
};

export function CaseList({ organizationId, cases }: CaseListProps) {
  const searchId = useId();
  const searchRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState("");
  const [role, setRole] = useState<RoleFilter>("all");
  const [sort, setSort] = useState<Sort>("recent");
  const deferredQuery = useDeferredValue(query);

  // Atajo "/" para buscar, como en la mayoría de herramientas de trabajo.
  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      const target = event.target as HTMLElement | null;
      const typing = target?.closest("input, textarea, select, [contenteditable=true]");
      if (event.key === "/" && !typing) {
        event.preventDefault();
        searchRef.current?.focus();
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const visible = useMemo(() => {
    const needle = normalize(deferredQuery.trim());
    const filtered = cases.filter((item) => {
      if (role !== "all" && item.my_role !== role) return false;
      if (!needle) return true;
      return normalize(`${item.reference} ${item.title}`).includes(needle);
    });
    return [...filtered].sort((a, b) =>
      sort === "title" ? a.title.localeCompare(b.title, "es") : b.created_at.localeCompare(a.created_at),
    );
  }, [cases, deferredQuery, role, sort]);

  return (
    <div>
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
        <div className="relative flex-1">
          <label htmlFor={searchId} className="sr-only">
            Buscar casos
          </label>
          <IconSearch className="pointer-events-none absolute top-1/2 left-3.5 size-4 -translate-y-1/2 text-text-subtle" />
          <input
            ref={searchRef}
            id={searchId}
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Buscar por título o referencia"
            className="block w-full rounded-lg border border-border-strong bg-background py-2.5 pr-12 pl-10 text-sm placeholder:text-text-subtle focus:outline-none focus-visible:outline-2 focus-visible:outline-accent"
          />
          <kbd className="pointer-events-none absolute top-1/2 right-3 hidden -translate-y-1/2 rounded border border-border px-1.5 font-mono text-xs text-text-subtle sm:block">
            /
          </kbd>
        </div>

        <fieldset className="flex flex-wrap items-center gap-2">
          <legend className="sr-only">Filtrar por su rol en el caso</legend>
          {ROLE_FILTERS.map((option) => (
            <label
              key={option.value}
              className="cursor-pointer rounded-full border border-border px-3 py-1.5 text-sm text-text-muted transition-colors hover:border-border-strong has-checked:border-accent has-checked:bg-accent/15 has-checked:text-text has-focus-visible:outline-2 has-focus-visible:outline-accent"
            >
              <input
                type="radio"
                name="role"
                value={option.value}
                checked={role === option.value}
                onChange={() => setRole(option.value)}
                className="sr-only"
              />
              {option.label}
            </label>
          ))}
        </fieldset>

        <label className="flex items-center gap-2 text-sm text-text-muted">
          Ordenar
          <select
            value={sort}
            onChange={(event) => setSort(event.target.value as Sort)}
            className="rounded-lg border border-border-strong bg-background px-3 py-2 text-sm text-text focus:outline-none focus-visible:outline-2 focus-visible:outline-accent"
          >
            <option value="recent">Más recientes</option>
            <option value="title">Título (A–Z)</option>
          </select>
        </label>
      </div>

      <p aria-live="polite" className="mt-6 text-sm text-text-subtle">
        {visible.length === cases.length
          ? `${cases.length} ${cases.length === 1 ? "caso" : "casos"}`
          : `${visible.length} de ${cases.length} casos`}
      </p>

      {visible.length === 0 ? (
        <div className="mt-4 rounded-2xl border border-dashed border-border-strong p-10 text-center">
          <p className="font-medium">Ningún caso coincide con la búsqueda.</p>
          <button
            type="button"
            onClick={() => {
              setQuery("");
              setRole("all");
            }}
            className="mt-3 text-sm text-accent hover:underline"
          >
            Quitar filtros
          </button>
        </div>
      ) : (
        <ul className="mt-4 divide-y divide-border overflow-hidden rounded-2xl border border-border bg-card/40">
          {visible.map((item) => (
            <li key={item.id}>
              <Link
                href={`/app/${organizationId}/cases/${item.id}`}
                className="group flex items-center gap-4 p-5 transition-colors hover:bg-card"
              >
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-xs text-accent">{item.reference}</span>
                    {item.status.toLowerCase() !== "active" && <Badge>{caseStatusLabel(item.status)}</Badge>}
                  </div>
                  <p className="mt-1 truncate font-medium">{item.title}</p>
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
      )}
    </div>
  );
}
