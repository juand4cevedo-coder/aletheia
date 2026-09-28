import { redirect } from "next/navigation";

import { listOrganizations } from "@/features/workspace/data";
import { requireUser } from "@/lib/auth/dal";

/** `/app` lleva a la primera organización del usuario. */
export default async function AppIndexPage() {
  await requireUser();
  const organizations = await listOrganizations();
  const first = organizations[0];

  if (first) {
    redirect(`/app/${first.id}`);
  }

  return (
    <main className="mx-auto max-w-lg px-6 py-24 text-center">
      <h1 className="text-2xl font-semibold">Sin organizaciones</h1>
      <p className="mt-3 text-text-muted">
        Su cuenta no pertenece a ninguna organización. Pida a un administrador
        de su firma que le dé acceso.
      </p>
    </main>
  );
}
