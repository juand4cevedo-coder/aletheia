import type { ReactNode } from "react";

type BadgeProps = {
  children: ReactNode;
  tone?: "neutral" | "accent" | "success";
};

const TONES = {
  neutral: "border-border-strong text-text-muted",
  accent: "border-accent/50 text-accent",
  success: "border-success/40 text-success",
} as const;

export function Badge({ children, tone = "neutral" }: BadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs whitespace-nowrap ${TONES[tone]}`}>
      {children}
    </span>
  );
}
