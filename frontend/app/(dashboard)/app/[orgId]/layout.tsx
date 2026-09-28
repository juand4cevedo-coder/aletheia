import { Sidebar } from "@/features/workspace/sidebar";
import { getOrganization, listOrganizations } from "@/features/workspace/data";
import { requireUser } from "@/lib/auth/dal";

export default async function OrganizationLayout({ children, params }: LayoutProps<"/app/[orgId]">) {
  const { orgId } = await params;
  const user = await requireUser();
  const [organization, organizations] = await Promise.all([
    getOrganization(orgId),
    listOrganizations(),
  ]);

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[17rem_1fr]">
      <Sidebar organization={organization} organizations={organizations} user={user} />
      <div className="min-w-0">{children}</div>
    </div>
  );
}
