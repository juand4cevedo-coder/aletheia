"use client";

import Link from "next/link";
import { useId, useState } from "react";

import { buttonStyles } from "@/components/ui/button-styles";

import {
    ANNUAL_BILLED_MONTHS,
    PLANS,
    SALES_EMAIL,
    formatCop,
    recommendPlan,
    type Plan,
} from "./plans";

type Billing = "monthly" | "annual";

const MAX_SLIDER_USERS = 20;

export function PricingExplorer() {
    const [billing, setBilling] = useState<Billing>("monthly");
    const [users, setUsers] = useState(3);
    const sliderId = useId();
    const recommended = recommendPlan(users);
    const usersLabel =
        users >= MAX_SLIDER_USERS ? `${MAX_SLIDER_USERS} o más personas` : users === 1 ? "1 persona" : `${users} personas`;

    return (
        <div>
            <div className="grid gap-6 rounded-2xl border border-border bg-elevated p-6 sm:p-8 lg:grid-cols-[1fr_auto] lg:items-end lg:gap-12">
                <div>
                    <div className="flex items-baseline justify-between gap-4">
                        <label htmlFor={sliderId} className="font-medium">
                            ¿Cuántas personas usarán Aletheia?
                        </label>
                        <output htmlFor={sliderId} className="font-mono text-sm text-accent">
                            {usersLabel}
                        </output>
                    </div>
                    <input
                        id={sliderId}
                        type="range"
                        min={1}
                        max={MAX_SLIDER_USERS}
                        value={users}
                        onChange={(event) => setUsers(Number(event.target.value))}
                        aria-valuetext={usersLabel}
                        className="mt-4 w-full cursor-pointer accent-accent"
                    />
                    <p className="mt-3 text-sm text-text-muted">
                        El plan marcado como recomendado cambia según el tamaño de su equipo.
                    </p>
                </div>

                <fieldset>
                    <legend className="sr-only">Periodo de facturación</legend>
                    <div className="inline-flex rounded-xl border border-border-strong p-1">
                        {(
                            [
                                { value: "monthly", label: "Mensual" },
                                { value: "annual", label: "Anual" },
                            ] as const
                        ).map((option) => (
                            <label
                                key={option.value}
                                className="relative cursor-pointer rounded-lg px-4 py-2 text-sm text-text-muted transition-colors has-checked:bg-accent has-checked:text-on-accent has-focus-visible:outline-2 has-focus-visible:outline-accent"
                            >
                                <input
                                    type="radio"
                                    name="billing"
                                    value={option.value}
                                    checked={billing === option.value}
                                    onChange={() => setBilling(option.value)}
                                    className="sr-only"
                                />
                                {option.label}
                            </label>
                        ))}
                    </div>
                    <p className="mt-2 text-xs text-success">
                        Anual: {12 - ANNUAL_BILLED_MONTHS} meses sin costo
                    </p>
                </fieldset>
            </div>

            <ul className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {PLANS.map((plan) => (
                    <li key={plan.id} className="flex">
                        <PlanCard plan={plan} billing={billing} recommended={plan.id === recommended} />
                    </li>
                ))}
            </ul>
        </div>
    );
}

type PlanCardProps = {
    plan: Plan;
    billing: Billing;
    recommended: boolean;
};

function PlanCard({ plan, billing, recommended }: PlanCardProps) {
    const custom = plan.monthlyPrice === null;

    return (
        <article
            aria-label={recommended ? `${plan.name}, recomendado para su equipo` : plan.name}
            className={`flex w-full flex-col rounded-2xl border p-6 transition-colors duration-300 ${recommended
                    ? "border-accent bg-card shadow-[0_0_0_1px_var(--accent),0_24px_60px_-24px_color-mix(in_oklab,var(--accent)_45%,transparent)]"
                    : "border-border bg-card/50"
                }`}
        >
            <div className="flex min-h-7 items-center justify-between gap-3">
                <h3 className="text-lg font-semibold">{plan.name}</h3>
                {recommended && (
                    <span className="rounded-full bg-accent px-2.5 py-0.5 text-xs font-medium text-on-accent">
                        Recomendado
                    </span>
                )}
            </div>
            <p className="mt-3 min-h-18 text-sm leading-6 text-text-muted">{plan.audience}</p>

            <div className="mt-6 min-h-20">
                {custom ? (
                    <>
                        <p className="text-3xl font-semibold tracking-tight">A medida</p>
                        <p className="mt-1 text-sm text-text-subtle">Según capacidad y condiciones</p>
                    </>
                ) : (
                    <Price monthly={plan.monthlyPrice ?? 0} billing={billing} />
                )}
            </div>

            <ul className="mt-6 flex-1 space-y-3 border-t border-border pt-6 text-sm">
                {plan.highlights.map((item) => (
                    <li key={item} className="flex gap-3">
                        <svg
                            aria-hidden="true"
                            viewBox="0 0 16 16"
                            className="mt-0.5 size-4 shrink-0 text-accent"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                        >
                            <path d="m3.5 8.5 3 3 6-7" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                        <span className="text-text-muted">{item}</span>
                    </li>
                ))}
            </ul>

            {custom ? (
                <Link
                    href={`mailto:${SALES_EMAIL}?subject=${encodeURIComponent("Plan Enterprise de Aletheia")}`}
                    className={`${buttonStyles("secondary")} mt-8 w-full`}
                >
                    Solicitar propuesta
                </Link>
            ) : (
                <Link
                    href={`/register?plan=${plan.id}`}
                    className={`${buttonStyles(recommended ? "primary" : "secondary")} mt-8 w-full`}
                >
                    Comenzar con {plan.name}
                </Link>
            )}
        </article>
    );
}

function Price({ monthly, billing }: { monthly: number; billing: Billing }) {
    if (billing === "monthly") {
        return (
            <>
                <p className="text-3xl font-semibold tracking-tight">
                    {formatCop(monthly)}
                    <span className="ml-1.5 text-sm font-normal text-text-subtle">/ mes</span>
                </p>
                <p className="mt-1 text-sm text-text-subtle">Facturación mensual</p>
            </>
        );
    }

    const yearly = monthly * ANNUAL_BILLED_MONTHS;
    return (
        <>
            <p className="text-3xl font-semibold tracking-tight">
                {formatCop(Math.round(yearly / 12))}
                <span className="ml-1.5 text-sm font-normal text-text-subtle">/ mes</span>
            </p>
            <p className="mt-1 text-sm text-text-subtle">
                {formatCop(yearly)} al año{" "}
                <span className="text-success">(ahorra {formatCop(monthly * 12 - yearly)})</span>
            </p>
        </>
    );
}