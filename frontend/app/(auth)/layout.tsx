import { Logo } from "@/components/brand/logo";
import { AuthShowcase } from "@/features/auth/auth-showcase";

export default function AuthLayout({ children }: LayoutProps<"/">) {
    return (
        <div className="grid min-h-screen flex-1 lg:grid-cols-[1fr_1.05fr]">
            <aside className="hidden border-r border-border bg-[radial-gradient(50rem_30rem_at_0%_0%,color-mix(in_oklab,var(--brand)_28%,transparent),transparent)] bg-elevated lg:block">
                <AuthShowcase />
            </aside>
            <div className="flex flex-col px-6 py-8 sm:px-10">
                <Logo />
                <main className="flex flex-1 items-center justify-center py-12">
                    <div className="w-full max-w-md">{children}</div>
                </main>
            </div>
        </div>
    );
}