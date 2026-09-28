"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { IconFolder, IconHome } from "@/components/ui/icons";

type SidebarNavProps = {
  organizationId: string;
};

export function SidebarNav({ organizationId }: SidebarNavProps) {
  const pathname = usePathname();
  const base = `/app/${organizationId}`;
  const items = [
    { href: base, label: "Inicio", icon: IconHome, active: pathname === base },
    { href: `${base}/cases`, label: "Casos", icon: IconFolder, active: pathname.startsWith(`${base}/cases`) },
  ];

  return (
    <nav aria-label="Área de trabajo">
      <ul className="space-y-1">
        {items.map((item) => (
          <li key={item.href}>
            <Link
              href={item.href}
              aria-current={item.active ? "page" : undefined}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                item.active ? "bg-card text-text" : "text-text-muted hover:bg-card/60 hover:text-text"
              }`}
            >
              <item.icon className={`size-4 ${item.active ? "text-accent" : ""}`} />
              {item.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
